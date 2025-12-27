#!/usr/bin/env python3
"""
Clean up script to delete all documents from Qdrant collection.
Use this before re-uploading documents to avoid duplicates.
"""
from qdrant_client import QdrantClient

def clear_collection():
    """Delete all points from the finance_documents collection."""
    client = QdrantClient(host="localhost", port=6333)
    
    try:
        # Get collection info
        info = client.get_collection("finance_documents")
        print(f"Current points in collection: {info.points_count}")
        
        if info.points_count == 0:
            print("Collection is already empty!")
            return
        
        # Confirm deletion
        response = input(f"\nAre you sure you want to delete all {info.points_count} points? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return
        
        # Delete all points by recreating the collection
        from qdrant_client.models import Distance, VectorParams
        
        print("\nDeleting collection...")
        client.delete_collection("finance_documents")
        
        print("Recreating collection...")
        client.create_collection(
            collection_name="finance_documents",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        
        print("✓ Collection cleared successfully!")
        print("You can now upload documents from the UI.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_collection()
