"""
FastAPI API server for secure finance LLM application.
Handles HTTP requests and orchestrates document retrieval and LLM queries.
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from pathlib import Path

from auth import verify_token, check_permissions
from retriever import retrieve_documents
from guardrails import validate_response
from logging import log_query

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
    user_id: str
    filters: Optional[dict] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    acl: Optional[str] = Form(None),
    user=Depends(verify_token)
):
    """
    Upload a PDF document for indexing.
    
    Args:
        file: PDF file to upload
        acl: Comma-separated list of user IDs who can access this document
        user: Authenticated user information
        
    Returns:
        Success message with file details
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check permissions (only admins can upload in this example)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload documents")
    
    try:
        # Save the file
        file_path = UPLOAD_DIR / file.filename
        
        # Check if file already exists
        if file_path.exists():
            raise HTTPException(status_code=400, detail="File already exists")
        
        # Write file to disk
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Parse ACL
        acl_list = [user_id.strip() for user_id in acl.split(",")] if acl else []
        
        # TODO: Trigger indexing pipeline
        # This would call ingest_pdfs.py and upsert_qdrant.py
        # For now, just save the file
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(contents),
            "acl": acl_list,
            "message": "File uploaded successfully. Run indexer to process."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    user=Depends(verify_token)
):
    """
    Process a user query with ACL filtering and guardrails.
    """
    # Check user permissions
    if not check_permissions(user, request.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Retrieve relevant documents
    documents = retrieve_documents(
        query=request.query,
        user_id=request.user_id,
        filters=request.filters
    )
    
    # Generate response (placeholder - integrate with LLM)
    answer = f"Response based on {len(documents)} documents"
    
    # Validate response with guardrails
    validated_answer = validate_response(answer, documents)
    
    # Log the query
    log_query(user_id=request.user_id, query=request.query, response=validated_answer)
    
    return QueryResponse(
        answer=validated_answer,
        sources=[{"id": doc.get("id"), "title": doc.get("title")} for doc in documents],
        confidence=0.85
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
