# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

# User 관련 스키마
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Run 관련 스키마
class RunBase(BaseModel):
    distance_km: float
    duration_seconds: int
    notes: Optional[str] = None

class RunCreate(RunBase):
    pass

class RunDisplay(RunBase):
    id: int
    user_id: int
    run_date: datetime

    class Config:
        from_attributes = True

# Report 관련 스키마
class ReportCreate(BaseModel):
    report_type: str # "daily" or "weekly"
    target_date: date