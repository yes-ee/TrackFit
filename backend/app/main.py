# app/main.py

from fastapi import FastAPI
from .routers import auth, runs, reports

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the TrackFit API"}