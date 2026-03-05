from faker import Faker  # type: ignore
import random
from datetime import datetime
import json
import time
import requests

fake = Faker()
API_URL = "http://127.0.0.1:8000/logs"

def generate_normal_log():
    return {
        "source_ip": fake.ipv4(),
        "destination_ip": fake.ipv4(),
        "port": random.choice([80, 443, 53, 22]),
        "protocol": random.choice(["TCP", "UDP"]),
        "bytes_sent": random.randint(40, 1500),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_port_scan(ip):
    return {
        "source_ip": ip,
        "destination_ip": fake.ipv4(),
        "port": random.randint(1, 1024),
        "protocol": "TCP",
        "bytes_sent": random.randint(40, 200),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_brute_force(ip):
    return {
        "source_ip": ip,
        "destination_ip": fake.ipv4(),
        "port": 22,  
        "protocol": "TCP",
        "bytes_sent": random.randint(40, 100),
        "timestamp": datetime.utcnow().isoformat()
    }

def send_log(log):
    try:
        response = requests.post(API_URL, json=log)
        print("Sent log:", response.status_code)
    except Exception as e:
        print("Error sending log:", e)

def main():
    port_scan_ip = fake.ipv4()
    brute_force_ip = fake.ipv4()

    while True:
        r = random.random()

        if r < 0.75:
            log = generate_normal_log()
        elif r < 0.9:
            log = generate_port_scan(port_scan_ip)
        else:
            log = generate_brute_force(brute_force_ip)

        print(json.dumps(log))
        send_log(log)
        time.sleep(0.2)
        


if __name__ == "__main__":
    main()