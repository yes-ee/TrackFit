# app/routers/reports.py

import os
import boto3
import json
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from .. import schemas, models, oauth2, crud
from typing import List

load_dotenv()

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
log = logging.getLogger("reports")

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
    log.info(f"crud.create_report_request start")
    # DB에 리포트 요청 기록 생성 -> PENDING으로 기록
    report_db = crud.create_report_request(db, report=report_request, user_id=current_user.id)
    log.info(f"crud.create_report_request end")
    log.info(f"Report request: {report_request}")
    log.info(f"Report request created: report_id={report_db.id}, user_id={current_user.id}, type={report_request.report_type}, date={report_request.target_date.isoformat()}")
    # SQS에 보낼 메시지 생성
    message_body = {
        "report_id": report_db.id,
        "user_id": current_user.id,
        "report_type": report_request.report_type,
        "target_date": report_request.target_date.isoformat()
    }

    # SQS 큐에 메시지 전송
    log.info(
        f"Queueing report request: report_id={report_db.id}, user_id={current_user.id}, "
        f"type={report_request.report_type}, date={report_request.target_date.isoformat()}"
    )

    sqs_client = boto3.client('sqs', region_name=AWS_REGION)

    response = sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message_body)
    )

    message_id = response.get("MessageId")
    log.info(
        f"Enqueued to SQS: message_id={message_id}, report_id={report_db.id}, queue_url={SQS_QUEUE_URL}"
    )

    return {"message": "Report generation has been requested and is being processed."}

@router.get("/", response_model=List[schemas.ReportDisplay])
def get_user_reports(
    db: Session = Depends(oauth2.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return crud.get_reports_by_user(db, user_id=current_user.id)