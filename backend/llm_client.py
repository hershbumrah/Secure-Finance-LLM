import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL", "llama2")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

def get_llm():
    """Get ChatOllama instance for text generation."""
    return ChatOllama(model=LLM_MODEL, base_url=LLM_BASE_URL, temperature=0.0)

def get_embeddings():
    """Get OllamaEmbeddings instance for vector embeddings."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=LLM_BASE_URL)

def embed_text(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector as list of floats
    """
    embeddings = get_embeddings()
    return embeddings.embed_query(text)

def embed_documents(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)

def generate_answer(query: str, context_documents: List[dict], num_unique_files: int = None) -> str:
    """
    Generate answer using LLM with RAG pattern.
    
    Args:
        query: User's question
        context_documents: Retrieved documents with content and metadata (text chunks)
        num_unique_files: Number of unique source document files the chunks come from
        
    Returns:
        Generated answer
    """
    from prompts import build_qa_prompt
    
    llm = get_llm()
    
    # Use the prompt builder from prompts.py
    prompt = build_qa_prompt(query, context_documents, num_unique_files)
    
    # Generate response with strong system message
    system_prompt = """You are a helpful financial assistant. Provide comprehensive, detailed answers by synthesizing information from the provided document excerpts. Remember that you may receive multiple text excerpts (chunks) from the same source document file. When referring to sources, be accurate about the number of unique documents vs the number of excerpts."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    return response.content

def test_llm():
    """Test LLM connectivity."""
    llm = get_llm()
    response = llm.invoke([HumanMessage(content="Say 'LLM is ready for assistance'")])
    return response.content