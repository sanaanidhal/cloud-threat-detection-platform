import redis
import json
import os
from dotenv import load_dotenv
import psycopg2
from collections import defaultdict
from datetime import datetime, timedelta
from app.ml_model import predict_anomaly
from app.metrics import logs_processed
from app.metrics import alerts_triggered

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
DATABASE_URL = os.getenv("DATABASE_URL")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Track activity
ip_activity = defaultdict(list)


def start_subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe("logs_channel")

    print("Listening for log events...")

    for message in pubsub.listen():
        if message["type"] == "message":
            log_data = json.loads(message["data"])
            process_log(log_data)

def process_log(log_data):
    source_ip = log_data["source_ip"]
    port = log_data["port"]
    bytes_sent = log_data["bytes_sent"]
    timestamp = datetime.utcnow()
    ip_activity[source_ip].append({
        "port": port,
        "timestamp": timestamp
    })

    # Clean old entries 
    ip_activity[source_ip] = [
        entry for entry in ip_activity[source_ip]
        if entry["timestamp"] > timestamp - timedelta(seconds=30)
    ]

    detect_port_scan(source_ip)
    detect_bruteforce(source_ip)
    detect_large_transfer(source_ip, bytes_sent)
    detect_ml_anomaly(source_ip, port, bytes_sent)

    logs_processed.inc()


def detect_port_scan(ip):
    recent = [
        entry for entry in ip_activity[ip]
        if entry["timestamp"] > datetime.utcnow() - timedelta(seconds=10)
    ]

    unique_ports = {entry["port"] for entry in recent}

    if len(unique_ports) > 10:
        create_alert(ip, "PORT_SCAN", "HIGH")
    
def create_alert(source_ip, alert_type, severity):
    conn = psycopg2.connect(DATABASE_URL)

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO alerts (source_ip, alert_type, severity) VALUES (%s, %s, %s)",
        (source_ip, alert_type, severity)
    )

    conn.commit()
    alerts_triggered.labels(
    severity=severity,
    type=alert_type
    ).inc()
    
    print("ALERT INSERTED INTO DB")
    cur.close()
    conn.close()

def detect_bruteforce(ip):
    recent = [
        entry for entry in ip_activity[ip]
        if entry["timestamp"] > datetime.utcnow() - timedelta(seconds=10)
        and entry["port"] == 22
    ]

    if len(recent) == 6:
        create_alert(ip, "BRUTE_FORCE", "HIGH")
        print(f"🚨 BRUTE FORCE DETECTED from {ip}")
        

def detect_large_transfer(ip, bytes_sent):
    if bytes_sent > 5000:
        print(f"🚨 LARGE DATA TRANSFER from {ip}")
        create_alert(ip, "LARGE_DATA_TRANSFER", "MEDIUM")

def detect_ml_anomaly(ip, port, bytes_sent):

    now = datetime.utcnow()

    # requests in last 10 seconds
    recent_requests = [
        entry for entry in ip_activity[ip]
        if entry["timestamp"] > now - timedelta(seconds=10)
    ]

    request_rate = len(recent_requests)

    is_anomaly = predict_anomaly(port, bytes_sent, request_rate)

    if is_anomaly:
        print(f"🚨 ML ANOMALY DETECTED from {ip}")
        create_alert(ip, "ML_ANOMALY", "MEDIUM")