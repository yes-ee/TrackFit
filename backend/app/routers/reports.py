# app/routers/reports.py

import os
import boto3
import json
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from .. import schemas, models, oauth2, crud

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

router = APIRouter(
    tags=["Reports"],
    prefix="/reports"
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
def request_report(
    report_request: schemas.ReportCreate,
    db: Session = Depends(oauth2.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # DB에 리포트 요청 기록 생성 -> PENDING으로 기록
    report_db = crud.create_report_request(db, report=report_request, user_id=current_user.id)

    # SQS에 보낼 메시지 생성
    message_body = {
        "report_id": report_db.id,
        "user_id": current_user.id,
        "report_type": report_request.report_type,
        "target_date": report_request.target_date.isoformat()
    }

    # SQS 큐에 메시지 전송
    sqs_client = boto3.client('sqs')
    sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message_body)
    )

    return {"message": "Report generation has been requested and is being processed."}