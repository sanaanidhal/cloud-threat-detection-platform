from fastapi import FastAPI
import threading
from .redis_subscriber import start_subscriber
from prometheus_client import generate_latest
from fastapi.responses import Response

app = FastAPI(title="Detection Service")

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_subscriber, daemon=True)
    thread.start()

@app.get("/")
def root():
    return {"message": "Detection service running"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")