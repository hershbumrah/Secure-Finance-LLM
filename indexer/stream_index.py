#!/usr/bin/env python3
"""Stream-based PDF processing to avoid memory issues."""
import sys
from pathlib import Path
import gc
import hashlib

sys.path.append(str(Path(__file__).parent.parent / "backend"))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from llm_client import embed_text
import PyPDF2

def generate_point_id(doc_id: str, page_num: int, chunk_idx: int) -> int:
    """Generate integer point ID from components."""
    # Create unique string and hash to integer
    id_string = f"{doc_id}_{page_num}_{chunk_idx}"
    hash_value = int(hashlib.md5(id_string.encode()).hexdigest()[:15], 16)
    # Ensure positive 64-bit integer
    return hash_value % (2**63)

def process_pdf_streaming(pdf_path: Path, upserter, user_id: str = "admin"):
    """Process PDF page by page to conserve memory."""
    print(f"\nProcessing: {pdf_path.name}")
    doc_id = hashlib.md5(pdf_path.name.encode()).hexdigest()
    
    total_inserted = 0
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"  Total pages: {total_pages}")
            
            for page_num in range(total_pages):
                try:
                    # Extract text from single page
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if not text or len(text.strip()) < 50:
                        continue
                    
                    # Create chunks from page (smaller chunks to avoid context length issues)
                    chunks = []
                    words = text.split()
                    chunk_size_words = 50  # Reduced from 100 to avoid context length errors
                    
                    for i in range(0, len(words), chunk_size_words):
                        chunk = " ".join(words[i:i + chunk_size_words])
                        if chunk.strip() and len(chunk) > 30:  # Skip very short chunks
                            chunks.append(chunk)
                    
                    # Process chunks immediately
                    for chunk_idx, chunk in enumerate(chunks):
                        try:
                            # Generate embedding
                            vector = embed_text(chunk)
                            
                            # Create integer point ID
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
                                    "acl": [user_id]
                                }
                            )
                            
                            # Insert single point
                            upserter.client.upsert(
                                collection_name=upserter.collection_name,
                                points=[point]
                            )
                            
                            total_inserted += 1
                            
                        except Exception as e:
                            print(f"    Error on page {page_num+1}, chunk {chunk_idx}: {e}")
                    
                    # Progress update every 10 pages
                    if (page_num + 1) % 10 == 0:
                        print(f"  Progress: {page_num + 1}/{total_pages} pages ({total_inserted} chunks)")
                        gc.collect()  # Force garbage collection
                        
                except Exception as e:
                    print(f"  Error on page {page_num + 1}: {e}")
                    continue
        
        print(f"  ✓ Completed: {total_inserted} chunks indexed")
        return total_inserted
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return total_inserted


class SimpleUpserter:
    """Simple Qdrant wrapper."""
    def __init__(self, host="localhost", port=6333, collection_name="finance_documents", vector_size=384):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Ensure collection exists
        try:
            collections = self.client.get_collections().collections
            if collection_name not in [c.name for c in collections]:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                print(f"Created collection: {collection_name}")
        except Exception as e:
            print(f"Collection setup: {e}")


def main():
    pdf_dir = Path(__file__).parent.parent / "data" / "pdfs"
    pdf_files = sorted(list(pdf_dir.glob("*.pdf")))
    
    print(f"Found {len(pdf_files)} PDFs\n")
    
    # Initialize
    upserter = SimpleUpserter()
    
    total_all = 0
    for pdf in pdf_files:
        count = process_pdf_streaming(pdf, upserter)
        total_all += count
        gc.collect()
    
    print(f"\n{'='*50}")
    print(f"✅ Total indexed: {total_all} chunks")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
