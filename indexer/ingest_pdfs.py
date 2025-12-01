"""
PDF document ingestion with chunking and metadata tagging.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
from datetime import datetime


def ingest_pdfs(
    pdf_directory: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    acl_mapping: Optional[Dict[str, List[str]]] = None
) -> List[Dict]:
    """
    Ingest PDF files, chunk them, and add metadata tags.
    
    Args:
        pdf_directory: Path to directory containing PDF files
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between chunks in characters
        acl_mapping: Mapping of document IDs to user IDs for ACL
        
    Returns:
        List of processed document chunks with metadata
    """
    pdf_path = Path(pdf_directory)
    if not pdf_path.exists():
        raise ValueError(f"Directory not found: {pdf_directory}")
    
    all_chunks = []
    pdf_files = list(pdf_path.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        
        # Generate document metadata
        doc_id = generate_document_id(pdf_file)
        metadata = extract_metadata(pdf_file, text)
        
        # Get ACL for this document
        acl = acl_mapping.get(doc_id, []) if acl_mapping else []
        
        # Chunk the document
        chunks = chunk_text(text, chunk_size, chunk_overlap)
        
        # Create chunk objects with metadata
        for i, chunk in enumerate(chunks):
            chunk_obj = {
                "id": f"{doc_id}_chunk_{i}",
                "document_id": doc_id,
                "chunk_index": i,
                "content": chunk,
                "title": pdf_file.stem,
                "acl": acl,
                "metadata": {
                    **metadata,
                    "chunk_total": len(chunks),
                    "file_path": str(pdf_file)
                }
            }
            all_chunks.append(chunk_obj)
    
    print(f"Generated {len(all_chunks)} chunks from {len(pdf_files)} documents")
    return all_chunks


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text content
    """
    try:
        # Try using PyPDF2
        import PyPDF2
        
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text.strip()
        
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between consecutive chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings near the chunk boundary
            search_end = min(end + 100, text_length)
            sentence_end = text.rfind('. ', start, search_end)
            
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - chunk_overlap
    
    return chunks


def extract_metadata(pdf_path: Path, text: str) -> Dict:
    """
    Extract metadata from PDF file and content.
    
    Args:
        pdf_path: Path to PDF file
        text: Extracted text content
        
    Returns:
        Dictionary of metadata
    """
    stat = pdf_path.stat()
    
    metadata = {
        "filename": pdf_path.name,
        "file_size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "word_count": len(text.split()),
        "char_count": len(text),
    }
    
    # Extract document type/category from filename or content
    metadata["document_type"] = classify_document(pdf_path.name, text)
    
    return metadata


def classify_document(filename: str, text: str) -> str:
    """
    Classify document based on filename and content.
    
    Args:
        filename: PDF filename
        text: Document text
        
    Returns:
        Document category/type
    """
    filename_lower = filename.lower()
    text_lower = text.lower()
    
    # Simple keyword-based classification
    if any(word in filename_lower for word in ["report", "annual", "quarterly"]):
        return "report"
    elif any(word in filename_lower for word in ["statement", "balance", "income"]):
        return "financial_statement"
    elif any(word in filename_lower for word in ["policy", "procedure"]):
        return "policy"
    elif any(word in text_lower for word in ["agreement", "contract"]):
        return "contract"
    else:
        return "general"


def generate_document_id(pdf_path: Path) -> str:
    """
    Generate a unique document ID based on file path and name.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Unique document ID
    """
    # Use hash of file path for consistent ID
    path_str = str(pdf_path.absolute())
    return hashlib.md5(path_str.encode()).hexdigest()[:16]


def load_acl_mapping(acl_file: str) -> Dict[str, List[str]]:
    """
    Load ACL mapping from file.
    
    Args:
        acl_file: Path to ACL mapping file (JSON format)
        
    Returns:
        Dictionary mapping document IDs to user ID lists
    """
    import json
    
    try:
        with open(acl_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading ACL file: {e}")
        return {}


if __name__ == "__main__":
    # Example usage
    pdf_dir = "./data/pdfs"
    acl_file = "./data/acl_mapping.json"
    
    # Load ACL mapping
    acl_mapping = load_acl_mapping(acl_file) if os.path.exists(acl_file) else None
    
    # Ingest PDFs
    chunks = ingest_pdfs(
        pdf_directory=pdf_dir,
        chunk_size=1000,
        chunk_overlap=200,
        acl_mapping=acl_mapping
    )
    
    print(f"Successfully processed {len(chunks)} chunks")
