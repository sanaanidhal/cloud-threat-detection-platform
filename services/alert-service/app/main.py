from fastapi import FastAPI
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app=FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg.connect(DATABASE_URL)


@app.get("/alerts")

def get_alerts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, source_ip, alert_type, severity, created_at
        FROM alerts
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    alerts = []
    for row in rows:
        alerts.append({
            "id": row[0],
            "source_ip": row[1],
            "alert_type": row[2],
            "severity": row[3],
            "created_at": row[4]
        })

    return alerts