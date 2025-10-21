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

# Report의 기본 필드
class ReportBase(BaseModel):
    report_type: str
    target_date: date

# Report 생성을 요청할 때 받을 데이터
class ReportCreate(ReportBase):
    pass

# API 응답으로 리포트 정보를 보여줄 때 사용할 데이터
class ReportDisplay(ReportBase):
    id: int
    user_id: int
    status: str
    content: Optional[dict] = None

    class Config:
        from_attributes = True