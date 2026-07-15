"""
Service to automatically index uploaded PDFs into Qdrant.
"""
import sys
from pathlib import Path
from typing import List, Optional
import hashlib
import PyPDF2
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, Filter
from llm_client import embed_text
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))



# Chunking defaults tuned for long financial reports.
CHUNK_SIZE_WORDS = int(os.getenv("CHUNK_SIZE_WORDS", "180"))
CHUNK_OVERLAP_WORDS = int(os.getenv("CHUNK_OVERLAP_WORDS", "40"))
MIN_CHUNK_WORDS = int(os.getenv("MIN_CHUNK_WORDS", "20"))


def chunk_words_with_overlap(words: List[str], chunk_size: int, overlap: int) -> List[str]:
    """Create overlapping word chunks for better long-document recall."""
    if not words:
        return []

    chunk_size = max(chunk_size, 50)
    overlap = max(min(overlap, chunk_size - 1), 0)
    step = chunk_size - overlap if chunk_size > overlap else chunk_size

    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) >= MIN_CHUNK_WORDS:
            chunks.append(" ".join(chunk_words))
        i += step
    return chunks


def generate_point_id(doc_id: str, page_num: int, chunk_idx: int) -> int:
    """Generate integer point ID from components."""
    id_string = f"{doc_id}_{page_num}_{chunk_idx}"
    hash_value = int(hashlib.md5(id_string.encode()).hexdigest()[:15], 16)
    return hash_value % (2**63)


def index_pdf_file(
    pdf_path: Path,
    acl_list: List[str],
    collection_name: str = "finance_documents",
    qdrant_host: str = QDRANT_HOST,
    qdrant_port: int = QDRANT_PORT
) -> dict:
    """
    Index a single PDF file into Qdrant with specified ACL.
    
    Args:
        pdf_path: Path to PDF file
        acl_list: List of user IDs who can access this document
        collection_name: Qdrant collection name
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
        
    Returns:
        Dictionary with indexing statistics
    """
    client = QdrantClient(host=qdrant_host, port=qdrant_port)
    doc_id = hashlib.md5(pdf_path.name.encode()).hexdigest()
    
    # Ensure collection exists
    try:
        collections = client.get_collections().collections
        if collection_name not in [c.name for c in collections]:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
    except Exception as e:
        print(f"Collection setup error: {e}")
    
    total_chunks = 0
    errors = 0
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            for page_num in range(total_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if not text or len(text.strip()) < 50:
                        continue
                    
                    # Create configurable overlapping chunks for long reports
                    words = text.split()
                    chunks = chunk_words_with_overlap(
                        words,
                        CHUNK_SIZE_WORDS,
                        CHUNK_OVERLAP_WORDS
                    )

                    for chunk_idx, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue
                        
                        try:
                            # Generate embedding
                            vector = embed_text(chunk)
                            
                            # Create point with ACL
                            point_id = generate_point_id(doc_id, page_num, chunk_idx)
                            point = PointStruct(
                                id=point_id,
                                vector=vector,
                                payload={
                                    "content": chunk,
                                    "source_file": pdf_path.name,
                                    "page_number": page_num + 1,
                                    "chunk_index": chunk_idx,
                                    "document_id": doc_id,
                                    "acl": acl_list  # Use provided ACL list
                                }
                            )
                            
                            # Insert into Qdrant
                            client.upsert(
                                collection_name=collection_name,
                                points=[point]
                            )
                            
                            total_chunks += 1
                            
                        except Exception as e:
                            errors += 1
                            print(f"Error on page {page_num+1}, chunk {chunk_idx}: {e}")
                
                except Exception as e:
                    errors += 1
                    print(f"Error on page {page_num + 1}: {e}")
        
        return {
            "status": "success",
            "filename": pdf_path.name,
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "errors": errors,
            "acl": acl_list
        }
        
    except Exception as e:
        return {
            "status": "error",
            "filename": pdf_path.name,
            "error": str(e)
        }
