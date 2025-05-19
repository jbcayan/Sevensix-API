from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.accounts.models.user import RoleEnum


# ────────────────────────────────────────────────────────────────────────────
# Base
# ────────────────────────────────────────────────────────────────────────────
class _UserBase(BaseModel):
    username: str = Field(..., examples=["johndoe"])
    email: EmailStr = Field(..., examples=["johndoe@example.com"])


# ────────────────────────────────────────────────────────────────────────────
# Admin‑facing payloads
# ────────────────────────────────────────────────────────────────────────────
class UserCreate(_UserBase):
    password: str = Field(..., min_length=8)
    role: Optional[RoleEnum] = None  # admin may set it; default handled server‑side

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "yourpassword",
                "role": "end_user",
            }
        }
    }


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[RoleEnum] = None


# ────────────────────────────────────────────────────────────────────────────
# Public payloads
# ────────────────────────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "johndoe@example.com",
                "password": "yourpassword",
            }
        }
    }


class UserOut(_UserBase):
    uid: UUID
    role: RoleEnum
    created_at: datetime

    model_config = dict(from_attributes=True)


# ────────────────────────────────────────────────────────────────────────────
# Auth
# ────────────────────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
                "token_type": "bearer",
            }
        }
    }


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[RoleEnum] = None