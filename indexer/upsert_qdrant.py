"""
Embed document chunks and insert into Qdrant vector database.
"""
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    CollectionStatus
)
import uuid


class QdrantUpserter:
    """Handle document embedding and insertion into Qdrant."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "finance_documents",
        vector_size: int = 1536  # OpenAI ada-002 dimension
    ):
        """
        Initialize Qdrant client and collection.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection
            vector_size: Dimension of embedding vectors
        """
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Create collection if it doesn't exist
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                print(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Collection '{self.collection_name}' created successfully")
            else:
                print(f"Collection '{self.collection_name}' already exists")
                
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise
    
    def upsert_documents(
        self,
        documents: List[Dict],
        batch_size: int = 100
    ) -> int:
        """
        Embed and upsert documents into Qdrant.
        
        Args:
            documents: List of document chunks with content and metadata
            batch_size: Number of documents to process in each batch
            
        Returns:
            Number of documents successfully inserted
        """
        total_inserted = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"Processing batch {i // batch_size + 1} ({len(batch)} documents)")
            
            try:
                # Generate embeddings for batch
                embeddings = self._embed_batch(batch)
                
                # Prepare points for insertion
                points = []
                for doc, embedding in zip(batch, embeddings):
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "content": doc.get("content", ""),
                            "title": doc.get("title", ""),
                            "document_id": doc.get("document_id", ""),
                            "chunk_index": doc.get("chunk_index", 0),
                            "acl": doc.get("acl", []),
                            "metadata": doc.get("metadata", {})
                        }
                    )
                    points.append(point)
                
                # Upsert to Qdrant
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                total_inserted += len(points)
                print(f"Successfully inserted {len(points)} documents")
                
            except Exception as e:
                print(f"Error processing batch: {e}")
                continue
        
        print(f"Total documents inserted: {total_inserted}")
        return total_inserted
    
    def _embed_batch(self, documents: List[Dict]) -> List[List[float]]:
        """
        Generate embeddings for a batch of documents.
        
        Args:
            documents: List of documents to embed
            
        Returns:
            List of embedding vectors
        """
        # Extract text content
        texts = [doc.get("content", "") for doc in documents]
        
        # Generate embeddings
        # TODO: Implement with your chosen embedding model
        embeddings = self._generate_embeddings(texts)
        
        return embeddings
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using embedding model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Note:
            Placeholder implementation. Replace with actual embedding model.
        """
        # Option 1: OpenAI Embeddings
        # import openai
        # response = openai.Embedding.create(
        #     input=texts,
        #     model="text-embedding-ada-002"
        # )
        # return [item['embedding'] for item in response['data']]
        
        # Option 2: Sentence Transformers
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # embeddings = model.encode(texts)
        # return embeddings.tolist()
        
        # Placeholder: Return dummy vectors
        print("Warning: Using dummy embeddings. Implement actual embedding generation.")
        return [[0.0] * self.vector_size for _ in texts]
    
    def get_collection_info(self) -> Dict:
        """
        Get information about the collection.
        
        Returns:
            Collection information dictionary
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
                "vector_size": self.vector_size
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}
    
    def delete_collection(self):
        """Delete the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' deleted")
        except Exception as e:
            print(f"Error deleting collection: {e}")


def main():
    """Main function to demonstrate usage."""
    import json
    from pathlib import Path
    
    # Initialize upserter
    upserter = QdrantUpserter(
        host="localhost",
        port=6333,
        collection_name="finance_documents"
    )
    
    # Example: Load processed documents from ingest_pdfs.py
    # In practice, you would pipe the output from ingest_pdfs directly
    documents_file = "processed_documents.json"
    
    if Path(documents_file).exists():
        with open(documents_file, 'r') as f:
            documents = json.load(f)
        
        # Upsert documents
        count = upserter.upsert_documents(documents, batch_size=100)
        print(f"Inserted {count} documents into Qdrant")
        
        # Show collection info
        info = upserter.get_collection_info()
        print(f"Collection info: {json.dumps(info, indent=2)}")
    else:
        print(f"Documents file not found: {documents_file}")
        print("Run ingest_pdfs.py first to generate documents")


if __name__ == "__main__":
    main()
