from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from . import models, schemas
from .redis_client import publish_log_event
from fastapi.encoders import jsonable_encoder

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
    db_log = models.Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Publish to Redis
    log_data = jsonable_encoder(log)
    publish_log_event(log_data)
    
    return db_log

@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    return db.query(models.Log).all()