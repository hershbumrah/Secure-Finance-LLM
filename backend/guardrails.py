"""
Hallucination prevention and response validation guardrails.
"""
from typing import List, Dict


def validate_response(answer: str, source_documents: List[Dict]) -> str:
    """
    Validate LLM response against source documents to prevent hallucinations.
    
    Args:
        answer: Generated answer from LLM
        source_documents: Documents used to generate the answer
        
    Returns:
        Validated (and possibly modified) answer
    """
    # Check if answer is grounded in source documents
    if not is_grounded(answer, source_documents):
        return add_uncertainty_disclaimer(answer)
    
    # Check for potential PII leakage
    if contains_pii(answer):
        return redact_pii(answer)
    
    # Check for financial compliance
    if not meets_compliance_standards(answer):
        return add_compliance_disclaimer(answer)
    
    return answer


def is_grounded(answer: str, documents: List[Dict]) -> bool:
    """
    Check if the answer is grounded in the provided documents.
    
    Args:
        answer: Generated answer
        documents: Source documents
        
    Returns:
        True if answer appears to be grounded in sources
    """
    # TODO: Implement more sophisticated grounding check
    # Could use:
    # - Semantic similarity between answer and document chunks
    # - Citation verification
    # - Fact extraction and verification
    
    if not documents:
        return False
    
    # Simple keyword overlap check (placeholder)
    doc_text = " ".join([doc.get("content", "") for doc in documents])
    answer_words = set(answer.lower().split())
    doc_words = set(doc_text.lower().split())
    
    overlap = len(answer_words.intersection(doc_words))
    overlap_ratio = overlap / len(answer_words) if answer_words else 0
    
    return overlap_ratio > 0.3  # At least 30% word overlap


def contains_pii(text: str) -> bool:
    """
    Check if text contains Personally Identifiable Information.
    
    Args:
        text: Text to check
        
    Returns:
        True if PII is detected
    """
    # TODO: Implement PII detection
    # Could use:
    # - Regex patterns for SSN, credit cards, etc.
    # - Named entity recognition
    # - PII detection models
    
    import re
    
    # Simple patterns (expand in production)
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    return bool(re.search(ssn_pattern, text) or re.search(email_pattern, text))


def redact_pii(text: str) -> str:
    """
    Redact PII from text.
    
    Args:
        text: Text containing PII
        
    Returns:
        Text with PII redacted
    """
    import re
    
    # Redact common PII patterns
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED-EMAIL]', text)
    
    return text


def meets_compliance_standards(answer: str) -> bool:
    """
    Check if answer meets financial compliance standards.
    
    Args:
        answer: Generated answer
        
    Returns:
        True if compliant
    """
    # TODO: Implement compliance checking
    # Could check for:
    # - Required disclaimers
    # - Prohibited advice
    # - Regulatory requirements
    
    return True  # Placeholder


def add_uncertainty_disclaimer(answer: str) -> str:
    """Add disclaimer for potentially ungrounded answers."""
    disclaimer = "\n\n[Note: This answer may not be fully supported by the available documents.]"
    return answer + disclaimer


def add_compliance_disclaimer(answer: str) -> str:
    """Add financial compliance disclaimer."""
    disclaimer = "\n\n[Disclaimer: This information is for educational purposes only and should not be considered financial advice.]"
    return answer + disclaimer
