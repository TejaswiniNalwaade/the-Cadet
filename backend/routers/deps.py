"""
Shared authentication dependencies for route protection.
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from jose import jwt, JWTError
from database import get_db
from models.models import User

SECRET_KEY = "ncc_secret_key_change_in_production"
ALGORITHM  = "HS256"


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Validate Bearer token and return the authenticated User."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, Exception):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Only allow users with role == 'admin'."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied: Admin role required"
        )
    return current_user


def require_admin_or_officer(current_user: User = Depends(get_current_user)) -> User:
    """Allow admin or officer roles (e.g. marking attendance, managing events)."""
    if current_user.role not in ("admin", "officer"):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Admin or Officer role required"
        )
    return current_user
