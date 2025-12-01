"""
Audit logging for compliance and monitoring.
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Set up audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# File handler for audit logs
audit_handler = logging.FileHandler(LOG_DIR / "audit.log")
audit_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
audit_logger.addHandler(audit_handler)

# Application logger
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)

app_handler = logging.FileHandler(LOG_DIR / "app.log")
app_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
app_logger.addHandler(app_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)
app_logger.addHandler(console_handler)


def log_query(
    user_id: str,
    query: str,
    response: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log user query for audit purposes.
    
    Args:
        user_id: User who made the query
        query: The query text
        response: The generated response
        metadata: Additional metadata to log
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "query",
        "user_id": user_id,
        "query": query,
        "response_length": len(response),
        "metadata": metadata or {}
    }
    
    audit_logger.info(json.dumps(log_entry))


def log_access(
    user_id: str,
    resource_id: str,
    action: str,
    success: bool,
    reason: Optional[str] = None
) -> None:
    """
    Log access attempts to resources.
    
    Args:
        user_id: User attempting access
        resource_id: Resource being accessed
        action: Action being performed (read, write, etc.)
        success: Whether access was granted
        reason: Reason for denial if not successful
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "access",
        "user_id": user_id,
        "resource_id": resource_id,
        "action": action,
        "success": success,
        "reason": reason
    }
    
    audit_logger.info(json.dumps(log_entry))


def log_error(
    error_type: str,
    error_message: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log application errors.
    
    Args:
        error_type: Type of error
        error_message: Error message
        context: Additional context about the error
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "error",
        "error_type": error_type,
        "error_message": error_message,
        "context": context or {}
    }
    
    app_logger.error(json.dumps(log_entry))


def log_system_event(
    event_type: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log system-level events.
    
    Args:
        event_type: Type of system event
        description: Event description
        metadata: Additional metadata
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "description": description,
        "metadata": metadata or {}
    }
    
    app_logger.info(json.dumps(log_entry))
