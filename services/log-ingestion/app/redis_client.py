import redis
import json
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def publish_log_event(log_data: dict):
    result = r.publish("logs_channel", json.dumps(log_data))
    print("Publish result:", result)