"""
LLM instruction templates and prompt engineering.
"""
from typing import List, Dict


def build_qa_prompt(query: str, context_documents: List[Dict], num_unique_files: int = None) -> str:
    """
    Build a question-answering prompt with context.
    
    Args:
        query: User's question
        context_documents: Relevant documents for context (these are text chunks)
        num_unique_files: Number of unique source documents the chunks come from
        
    Returns:
        Formatted prompt for LLM
    """
    context = format_context(context_documents)
    
    # Add note about chunks vs documents
    chunk_note = ""
    if num_unique_files:
        num_chunks = len(context_documents)
        chunk_note = f"\n\nNOTE: You are seeing {num_chunks} text excerpt(s) from {num_unique_files} source document(s). Multiple excerpts may come from the same document file.\n"
    
    prompt = f"""You are a helpful financial assistant. Answer the user's question comprehensively and in detail using the information in the context documents below.
{chunk_note}
Context Documents:
{context}

User Question: {query}

IMPORTANT Instructions:
- Provide a thorough, detailed answer with specific information from the documents
- Include relevant details, examples, and complete explanations
- When referring to sources, understand that multiple excerpts may be from the same document file
- Synthesize information naturally into a cohesive, informative response
- Use complete sentences with proper context and explanations
- Give comprehensive answers - don't be brief unless the question requires it

Answer:"""
    
    return prompt


def build_summarization_prompt(document: str, max_length: int = 200) -> str:
    """
    Build a document summarization prompt.
    
    Args:
        document: Document text to summarize
        max_length: Maximum summary length in words
        
    Returns:
        Formatted prompt for LLM
    """
    prompt = f"""Summarize the following financial document in approximately {max_length} words or less. Focus on key facts, figures, and conclusions.

Document:
{document}

Summary:"""
    
    return prompt


def build_extraction_prompt(document: str, fields: List[str]) -> str:
    """
    Build a structured information extraction prompt.
    
    Args:
        document: Document text to extract from
        fields: Fields to extract
        
    Returns:
        Formatted prompt for LLM
    """
    fields_str = ", ".join(fields)
    
    prompt = f"""Extract the following information from the document: {fields_str}

Document:
{document}

Instructions:
- Extract only the requested fields
- Use "Not found" if a field is not present in the document
- Be precise and accurate
- Use the exact values from the document

Extracted Information:"""
    
    return prompt


def build_classification_prompt(text: str, categories: List[str]) -> str:
    """
    Build a text classification prompt.
    
    Args:
        text: Text to classify
        categories: Possible categories
        
    Returns:
        Formatted prompt for LLM
    """
    categories_str = "\n".join([f"- {cat}" for cat in categories])
    
    prompt = f"""Classify the following text into one of these categories:

{categories_str}

Text:
{text}

Classification:"""
    
    return prompt


def format_context(documents: List[Dict]) -> str:
    """
    Format context documents for inclusion in prompts.
    
    Args:
        documents: List of documents with content and metadata
        
    Returns:
        Formatted context string
    """
    if not documents:
        return "No context documents available."
    
    formatted_docs = []
    for i, doc in enumerate(documents, 1):
        title = doc.get("title", f"Document {i}")
        content = doc.get("content", "")
        
        formatted_docs.append(f"[Document {i}: {title}]\n{content}\n")
    
    return "\n".join(formatted_docs)


# System prompts for different personas
SYSTEM_PROMPTS = {
    "financial_advisor": """You are a knowledgeable financial advisor. Provide clear, accurate information about financial topics while being careful to note that your responses are informational and not personalized financial advice.""",
    
    "compliance_officer": """You are a compliance officer helping to ensure regulatory adherence. Focus on accuracy, proper documentation, and flagging potential compliance issues.""",
    
    "analyst": """You are a financial analyst helping to interpret and analyze financial data. Provide objective, data-driven insights based on the available information.""",
    
    "educator": """You are a financial educator helping users understand financial concepts. Explain things clearly and simply, providing examples when helpful."""
}


def get_system_prompt(persona: str = "financial_advisor") -> str:
    """
    Get system prompt for a specific persona.
    
    Args:
        persona: Name of the persona
        
    Returns:
        System prompt text
    """
    return SYSTEM_PROMPTS.get(persona, SYSTEM_PROMPTS["financial_advisor"])
