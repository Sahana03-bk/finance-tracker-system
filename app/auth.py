import hashlib
import secrets
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models


# In-memory token store
# Example: {"randomtoken123": 1}
active_tokens = {}

# Swagger-compatible bearer auth
security = HTTPBearer()


# ----------------------------
# Database Dependency
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Password Helpers
# ----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


# ----------------------------
# Token Helpers
# ----------------------------
def create_token() -> str:
    return secrets.token_hex(16)


def login_user(db: Session, username: str, password: str) -> Optional[str]:
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    token = create_token()
    active_tokens[token] = user.id
    return token


# ----------------------------
# Current User Helper
# ----------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    user_id = active_tokens.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ----------------------------
# Role-Based Access Helpers
# ----------------------------
def require_roles(allowed_roles: list):
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action"
            )
        return current_user
    return role_checker