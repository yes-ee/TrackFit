# app/routers/runs.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, oauth2, crud

router = APIRouter(
    tags=["Runs"],
    prefix="/runs"
)

@router.post("/", response_model=schemas.RunDisplay, status_code=status.HTTP_201_CREATED)
def create_new_run(
    run: schemas.RunCreate,
    db: Session = Depends(oauth2.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return crud.create_run(db=db, run=run, user_id=current_user.id)

@router.get("/", response_model=List[schemas.RunDisplay])
def get_all_runs_for_user(
    db: Session = Depends(oauth2.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    skip: int = 0,
    limit: int = 100
):
    return crud.get_runs_by_user(db, user_id=current_user.id, skip=skip, limit=limit)