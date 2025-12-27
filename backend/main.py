"""
FastAPI API server for secure finance LLM application.
Handles HTTP requests and orchestrates document retrieval and LLM queries.
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from pathlib import Path

from auth import verify_token, check_permissions, create_token
from retriever import retrieve_documents
from guardrails import validate_response
from audit_logging import log_query
from llm_client import test_llm, generate_answer
from indexer_service import index_pdf_file

# Configure upload directory
UPLOAD_DIR = Path(__file__).parent.parent / "data" / "pdfs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Secure Finance LLM API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    filters: Optional[dict] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: str
    role: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/health/llm")
def llm_health():
    return {"message": test_llm()}


@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    For demo purposes, accepts any credentials.
    In production, verify against a user database.
    """
    # TODO: Replace with actual user authentication
    # For demo: give everyone admin role to see all documents
    role = "admin"
    
    # Generate JWT token
    token = create_token(user_id=request.username, role=role)
    
    return LoginResponse(
        token=token,
        user_id=request.username,
        role=role
    )
    role: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/health/llm")
def llm_health():
    return {"message": test_llm()}


@app.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    acl: Optional[str] = Form(None),
    user=Depends(verify_token)
):
    """
    Upload a PDF document and automatically index it into Qdrant.
    
    Args:
        background_tasks: FastAPI background tasks
        file: PDF file to upload
        acl: Comma-separated list of user IDs who can access this document (defaults to admin)
        user: Authenticated user information
        
    Returns:
        Success message with file details and indexing status
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check permissions (only admins can upload)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload documents")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Save the file
        file_path = UPLOAD_DIR / file.filename
        
        # If file exists, delete old version from Qdrant first
        if file_path.exists():
            client = QdrantClient(host="localhost", port=6333)
            
            # Find and delete all points with this filename
            scroll_result = client.scroll(
                collection_name="finance_documents",
                scroll_filter=Filter(
                    should=[
                        FieldCondition(
                            key="source_file",
                            match=MatchValue(value=file.filename)
                        )
                    ]
                ),
                limit=10000,
                with_payload=False,
                with_vectors=False
            )
            
            point_ids = [point.id for point in scroll_result[0]]
            if point_ids:
                client.delete(
                    collection_name="finance_documents",
                    points_selector=point_ids
                )
        
        # Write file to disk (overwrites if exists)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Parse ACL (default to admin if not provided)
        acl_list = [user_id.strip() for user_id in acl.split(",")] if acl else ["admin"]
        
        # Trigger automatic indexing in background
        background_tasks.add_task(index_pdf_file, file_path, acl_list)
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(contents),
            "acl": acl_list,
            "message": "File uploaded and queued for indexing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/admin/documents")
async def list_documents(user=Depends(verify_token)):
    """
    List all documents in the system with their ACLs (admin only).
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        
        # Get all unique documents from Qdrant
        scroll_result = client.scroll(
            collection_name="finance_documents",
            limit=10000,
            with_payload=True,
            with_vectors=False
        )
        
        # Extract unique documents - deduplicate by BOTH document_id AND filename
        # This handles cases where old and new indexing methods coexist
        docs_dict = {}
        for point in scroll_result[0]:
            filename = point.payload.get("source_file")
            doc_id = point.payload.get("document_id")
            
            # Use filename as primary key for deduplication
            if filename and filename not in docs_dict:
                docs_dict[filename] = {
                    "document_id": doc_id or filename,  # Fallback to filename if no doc_id
                    "filename": filename,
                    "acl": point.payload.get("acl", [])
                }
        
        return {"documents": list(docs_dict.values())}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.get("/admin/users")
async def list_users(user=Depends(verify_token)):
    """
    List all known users in the system (admin only).
    For now, returns a simple list. In production, this would query a user database.
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # TODO: In production, query actual user database
    # For now, return hardcoded users + "admin"
    return {
        "users": [
            {"email": "admin", "name": "Administrator"},
            {"email": "user1@finance.com", "name": "User One"},
            {"email": "user2@finance.com", "name": "User Two"},
            {"email": "analyst@finance.com", "name": "Financial Analyst"}
        ]
    }


class UpdateACLRequest(BaseModel):
    document_id: str  # Can be document_id or filename
    acl: List[str]


@app.delete("/admin/document/{filename}")
async def delete_document(
    filename: str,
    user=Depends(verify_token)
):
    """
    Delete a document from Qdrant and filesystem (admin only).
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        import os
        
        client = QdrantClient(host="localhost", port=6333)
        
        # Find all points with this filename
        scroll_result = client.scroll(
            collection_name="finance_documents",
            scroll_filter=Filter(
                should=[
                    FieldCondition(
                        key="source_file",
                        match=MatchValue(value=filename)
                    )
                ]
            ),
            limit=10000,
            with_payload=True,
            with_vectors=False
        )
        
        # Delete all points with this filename
        point_ids = [point.id for point in scroll_result[0]]
        
        if point_ids:
            client.delete(
                collection_name="finance_documents",
                points_selector=point_ids
            )
        
        # Delete physical file
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            os.remove(file_path)
        
        return {
            "status": "success",
            "filename": filename,
            "deleted_chunks": len(point_ids),
            "file_deleted": file_path.exists() == False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@app.post("/admin/acl")
async def update_document_acl(
    request: UpdateACLRequest,
    user=Depends(verify_token)
):
    """
    Update ACL for a specific document (admin only).
    Updates all chunks associated with the document.
    Searches by both document_id and filename for compatibility.
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
        
        client = QdrantClient(host="localhost", port=6333)
        
        # Try to find points by document_id OR filename
        # This handles both old and new indexing methods
        scroll_result = client.scroll(
            collection_name="finance_documents",
            scroll_filter=Filter(
                should=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=request.document_id)
                    ),
                    FieldCondition(
                        key="source_file",
                        match=MatchValue(value=request.document_id)
                    )
                ]
            ),
            limit=10000,
            with_payload=True,
            with_vectors=False
        )
        
        # Update ACL for each point
        updated_count = 0
        for point in scroll_result[0]:
            # Update payload with new ACL
            client.set_payload(
                collection_name="finance_documents",
                payload={"acl": request.acl},
                points=[point.id]
            )
            updated_count += 1
        
        return {
            "status": "success",
            "document_id": request.document_id,
            "updated_chunks": updated_count,
            "new_acl": request.acl
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ACL: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    user=Depends(verify_token)
):
    """
    Process a user query with ACL filtering and guardrails.
    """
    user_id = user.get("user_id", "admin")
    user_role = user.get("role", "user")
    print(f"DEBUG: Query from user_id={user_id}, role={user_role}")
    
    # Retrieve relevant documents
    # Admins can see all documents, regular users filtered by ACL
    documents = retrieve_documents(
        query=request.query,
        user_id=user_id if user_role != "admin" else None,  # None = no ACL filter for admins
        filters=request.filters
    )
    
    print(f"DEBUG: Retrieved {len(documents)} documents")
    
    # Count unique source files
    unique_files = set()
    for doc in documents:
        if "source_file" in doc:
            unique_files.add(doc["source_file"])
    num_unique_files = len(unique_files)
    print(f"DEBUG: {len(documents)} chunks from {num_unique_files} unique files")
    
    # Generate response using LLM with retrieved context
    if documents:
        answer = generate_answer(request.query, documents, num_unique_files)
    else:
        answer = "I couldn't find any relevant documents to answer your question. Please ensure you have access to the necessary documents."
    
    # Validate response with guardrails
    validated_answer = validate_response(answer, documents)
    
    # Log the query
    log_query(user_id=user_id, query=request.query, response=validated_answer)
    
    # Deduplicate sources by filename
    seen_files = set()
    unique_sources = []
    for doc in documents:
        filename = doc.get("title") or doc.get("metadata", {}).get("source_file")
        if filename and filename not in seen_files:
            seen_files.add(filename)
            unique_sources.append({
                "id": str(doc.get("id")),
                "title": filename
            })
    
    return QueryResponse(
        answer=validated_answer,
        sources=unique_sources,
        confidence=0.85 if documents else 0.0
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
