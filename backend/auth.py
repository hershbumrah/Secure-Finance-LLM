"""
JWT validation and Role-Based Access Control (RBAC) implementation.
"""
from fastapi import HTTPException, Header
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os

# Load from environment variables (NEVER hardcode secrets!)
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE-THIS-SECRET-KEY-IN-PRODUCTION")
ALGORITHM = "HS256"


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify JWT token from Authorization header.
    
    Args:
        authorization: Bearer token from request header
        
    Returns:
        Decoded user information from token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")


def check_permissions(user: dict, requested_user_id: str) -> bool:
    """
    Check if user has permission to access requested resources.
    
    Args:
        user: Decoded user information from token
        requested_user_id: User ID being requested
        
    Returns:
        True if user has permission, False otherwise
    """
    # Admin users can access any resource
    if user.get("role") == "admin":
        return True
    
    # Regular users can only access their own resources
    return user.get("user_id") == requested_user_id


def create_token(user_id: str, role: str = "user") -> str:
    """
    Create a JWT token for a user.
    
    Args:
        user_id: Unique user identifier
        role: User role (user, admin, etc.)
        
    Returns:
        Encoded JWT token
    """
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
