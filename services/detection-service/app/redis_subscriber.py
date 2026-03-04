import redis
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def start_subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe("logs_channel")

    print("Listening for log events...")

    for message in pubsub.listen():
        if message["type"] == "message":
            log_data = json.loads(message["data"])
            process_log(log_data)

def process_log(log_data):
    print("Received log:", log_data)
    # Later we add anomaly detection here