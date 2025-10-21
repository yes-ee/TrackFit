import time
import json
import os
import boto3
import pandas as pd
from datetime import date, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, models
import logging

# .env 파일 로드 (로컬 개발 환경용)
load_dotenv()


SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger("worker")

def _generate_report_content(db: Session, user_id: int, target_date: date):
    """실제 DB에서 데이터를 조회하여 리포트 내용을 계산하는 함수"""
    start_time = pd.to_datetime(target_date)
    end_time = start_time + timedelta(days=1)

    runs_on_date = db.query(models.Run).filter(
        models.Run.user_id == user_id,
        models.Run.run_date >= start_time,
        models.Run.run_date < end_time
    ).all()

    if not runs_on_date:
        return {
            "date": target_date.isoformat(),
            "total_runs": 0,
            "message": "해당 날짜에 달리기 기록이 없습니다."
        }

    total_distance = sum(run.distance_km for run in runs_on_date)
    total_duration_seconds = sum(run.duration_seconds for run in runs_on_date)

    content = {
        "date": target_date.isoformat(),
        "total_runs": len(runs_on_date),
        "total_distance_km": float(total_distance),
        "total_duration_seconds": total_duration_seconds
    }
    return content

def process_messages():
    """SQS 큐를 확인하고 메시지를 처리하는 메인 함수"""
    sqs_client = boto3.client('sqs', region_name=AWS_REGION)


    log.info("Checking for messages in SQS queue...")
    log.info(f"SQS_QUEUE_URL: {SQS_QUEUE_URL}")
    try:
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=5, # 한 번에 여러 메시지 처리 가능
            WaitTimeSeconds=20
        )
    except Exception as e:
        log.error(f"Failed to receive message from SQS: {e}")
        return

    if "Messages" in response:
        for message in response["Messages"]:
            receipt_handle = message['ReceiptHandle']
            db = None
            body = None
            try:
                body = json.loads(message['Body'])
                report_id = body['report_id']
                user_id = body['user_id']
                target_date = date.fromisoformat(body['target_date'])
                
                log.info(f"Processing report_id: {report_id} for user_id: {user_id}")
                
                db = SessionLocal()
                
                report_content = _generate_report_content(db, user_id, target_date)
                log.info(f"Generated report content for report_id: {report_id}")
                crud.update_report_content(db, report_id, report_content, "COMPLETED")
                
                log.info(f"Report {report_id} completed successfully.")
                
                # 작업 성공 시 큐에서 메시지 삭제
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
            except Exception as e:
                report_id_str = f"report_id {body['report_id']}" if body else "Unknown report"
                log.error(f"Error processing message for {report_id_str}: {e}", exc_info=True)
                # 에러 발생 시 메시지를 삭제하지 않아 나중에 다시 처리됨
            finally:
                if db:
                    db.close()
                    log.info("Database session closed.")

if __name__ == "__main__":
    log.info("Starting Report Worker...")
    if not SQS_QUEUE_URL:
        log.error("CRITICAL: SQS_QUEUE_URL environment variable is not set. Worker exiting.")
    else:
        while True:
            process_messages()
            time.sleep(1)

