from faker import Faker 
import random
from datetime import datetime
import json
import time

fake = Faker()

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
        time.sleep(0.2)
        with open("generated_logs.json", "a") as f:
            f.write(json.dumps(log) + "\n")


if __name__ == "__main__":
    main()