"""
FastAPI API server for secure finance LLM application.
Handles HTTP requests and orchestrates document retrieval and LLM queries.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from auth import verify_token, check_permissions
from retriever import retrieve_documents
from guardrails import validate_response
from logging import log_query

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
