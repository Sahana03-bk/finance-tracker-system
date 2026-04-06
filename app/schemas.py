from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# ----------------------------
# User Schemas
# ----------------------------

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)
    role: str = Field(..., pattern="^(viewer|analyst|admin)$")


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = {
        "from_attributes": True
    }


# ----------------------------
# Transaction Schemas
# ----------------------------

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    category: str = Field(..., min_length=2, max_length=50)
    date: date
    note: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    category: str = Field(..., min_length=2, max_length=50)
    date: date
    note: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date
    note: Optional[str]
    user_id: int

    model_config = {
        "from_attributes": True
    }