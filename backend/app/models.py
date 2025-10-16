# app/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    BigInteger,
    ForeignKey,
    DECIMAL,
    DATE,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )

    runs = relationship("Run", back_populates="owner")
    reports = relationship("Report", back_populates="owner")


class Run(Base):
    __tablename__ = "runs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    run_date = Column(TIMESTAMP(timezone=True), nullable=False)
    distance_km = Column(DECIMAL(10, 2), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    avg_pace_seconds_per_km = Column(Integer)
    calories_burned = Column(Integer)
    notes = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="runs")


class Report(Base):
    __tablename__ = "reports"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(10), nullable=False)  # "daily", "weekly"
    target_date = Column(DATE, nullable=False)
    status = Column(
        String(20), nullable=False, default="PENDING"
    )  # PENDING, COMPLETED, FAILED
    content = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at = Column(TIMESTAMP(timezone=True))

    owner = relationship("User", back_populates="reports")