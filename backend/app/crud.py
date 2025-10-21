# app/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas, hashing
from datetime import datetime
from typing import List

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hashing.Hasher.get_password_hash(user.password)
    db_user = models.User(
        username=user.username, email=user.email, password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_run(db: Session, run: schemas.RunCreate, user_id: int):
    db_run = models.Run(
        **run.dict(),
        user_id=user_id,
        run_date=datetime.now()
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

def get_runs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Run).filter(models.Run.user_id == user_id).offset(skip).limit(limit).all()


# DB에 리포트 요청 기록 생성
# status는 기본적으로 "PENDING"
def create_report_request(db: Session, report: schemas.ReportCreate, user_id: int):
    db_report = models.Report(**report.dict(), user_id=user_id, status="PENDING")
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def update_report_content(db: Session, report_id: int, content: dict, status: str):
    db.query(models.Report).filter(models.Report.id == report_id).update({
        "content": content,
        "status": status,
        "completed_at": func.now()
    })
    db.commit()

def get_reports_by_user(db: Session, user_id: int) -> List[models.Report]:
    return db.query(models.Report).filter(models.Report.user_id == user_id).order_by(models.Report.target_date.desc()).all()