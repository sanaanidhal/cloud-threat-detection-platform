from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi import Depends
from . import models, schemas
from .database import engine, SessionLocal
from .redis_client import publish_log_event
from .metrics import logs_ingested
from prometheus_client import generate_latest

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Log Ingestion Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/logs", response_model=schemas.LogResponse)
def create_log(log: schemas.LogCreate, db: Session = Depends(get_db)):
    db_log = models.Log(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    publish_log_event(jsonable_encoder(db_log))
    logs_ingested.inc()     
    return db_log

@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    return db.query(models.Log).all()

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")