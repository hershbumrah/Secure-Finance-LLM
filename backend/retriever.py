"""
ACL-filtered document retrieval from vector database.
"""
from typing import List, Optional, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from llm_client import embed_text

# Initialize Qdrant client (configure connection in production)
client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "finance_documents"


def retrieve_documents(
    query: str,
    user_id: Optional[str] = None,
    filters: Optional[Dict] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Retrieve documents from vector database with ACL filtering.
    Diversifies results to include chunks from different source files when possible.
    
    Args:
        query: User's search query
        user_id: User ID for ACL filtering (None = no ACL filter, for admins)
        filters: Additional metadata filters
        limit: Maximum number of documents to return
        
    Returns:
        List of relevant documents with metadata
    """
    print(f"DEBUG retriever: Searching with user_id={user_id}")
    
    # Build ACL filter only if user_id is provided
    if user_id:
        acl_filter = Filter(
            must=[
                FieldCondition(
                    key="acl",
                    match=MatchValue(value=user_id)
                )
            ]
        )
    else:
        # No ACL filter for admins
        acl_filter = None
    
    # Add additional filters if provided
    if filters:
        if not acl_filter:
            acl_filter = Filter(must=[])
        for key, value in filters.items():
            acl_filter.must.append(
                FieldCondition(key=key, match=MatchValue(value=value))
            )
    try:
        # Generate query embedding
        query_vector = embed_text(query)
        
        # Retrieve more results initially for diversity
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=acl_filter,
            limit=limit * 3  # Get 3x to ensure diversity
        ).points
        
        # Diversify results: prefer one chunk per unique document
        documents = []
        seen_files = set()
        remaining_results = []
        
        # First pass: one chunk per unique file
        for result in results:
            source_file = result.payload.get("source_file", "")
            if source_file and source_file not in seen_files:
                seen_files.add(source_file)
                documents.append({
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "title": source_file,
                    "metadata": {
                        "page_number": result.payload.get("page_number"),
                        "source_file": source_file,
                        "chunk_index": result.payload.get("chunk_index")
                    },
                    "score": result.score
                })
            else:
                remaining_results.append(result)
            
            if len(documents) >= limit:
                break
        
        # Second pass: fill remaining slots with best matches
        for result in remaining_results:
            if len(documents) >= limit:
                break
            documents.append({
                "id": result.id,
                "content": result.payload.get("content", ""),
                "title": result.payload.get("source_file", ""),
                "metadata": {
                    "page_number": result.payload.get("page_number"),
                    "source_file": result.payload.get("source_file"),
                    "chunk_index": result.payload.get("chunk_index")
                },
                "score": result.score
            })
        
        print(f"DEBUG retriever: Returning {len(documents)} documents from {len(seen_files)} unique files")
        return documents
        
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        import traceback
        traceback.print_exc()
        return []
