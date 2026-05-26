from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserSignup(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan: str
    status: str
    trial_ends_at: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
