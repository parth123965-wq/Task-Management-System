from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.model.user import UserRole
import uuid
from datetime import datetime
from typing import Optional
from enum import Enum

class UserBase(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Alphanumeric, underscores, and hyphens only"
    )
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="Plaintext password for registration"
    )
    
class UserLogin(BaseModel):
    identifier: str = Field(
        ..., 
        description="Accepts either email or username"
    )
    password: str = Field(
        ..., 
        min_length=1, 
        max_length=128
    )
    
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    avatar_url: Optional[str] = Field(None, max_length=1024)
    
class UserResponse(UserBase):
    id: uuid.UUID
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 ORM mode configuration
    model_config = ConfigDict(from_attributes=True)
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"