# Cloud-Native Distributed Threat Detection Platform

![CI](https://github.com/sanaanidhal/cloud-threat-detection-platform/actions/workflows/ci.yml/badge.svg)

A production-grade security monitoring platform built with microservices architecture. Ingests network logs in real time, detects threats using both rule-based logic and machine learning, triggers alerts, and visualizes everything through a live Grafana dashboard.

Built as a portfolio project demonstrating distributed systems, ML integration, containerization, and observability engineering.

---

## Architecture

```
                        ┌─────────────────────────────────────────────────┐
                        │              Docker / Kubernetes                 │
                        │                                                  │
  HTTP POST             │  ┌─────────────────┐    Redis Pub/Sub            │
─────────────────────►  │  │  Log Ingestion  │ ──────────────────────►    │
  /logs                 │  │   Service :8000  │                            │
                        │  └────────┬────────┘    ┌──────────────────┐    │
                        │           │              │ Detection Service │    │
                        │           │ PostgreSQL   │     :8001        │    │
                        │           ▼              │                  │    │
                        │  ┌─────────────────┐    │ • Port Scan      │    │
                        │  │   PostgreSQL    │◄───│ • Brute Force    │    │
                        │  │   :5432         │    │ • Large Transfer │    │
                        │  └─────────────────┘    │ • ML Anomaly     │    │
                        │           ▲              └──────────────────┘    │
                        │           │                                      │
                        │  ┌─────────────────┐    ┌──────────────────┐    │
                        │  │  Alert Service  │    │   Prometheus     │    │
                        │  │    :8002        │    │     :9090        │    │
                        │  └─────────────────┘    └────────┬─────────┘    │
                        │                                   │              │
                        │                         ┌─────────▼─────────┐   │
                        │                         │     Grafana        │   │
                        │                         │     :3000          │   │
                        │                         └───────────────────┘   │
                        └─────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Services | FastAPI + Uvicorn |
| Database | PostgreSQL 15 |
| Message Broker | Redis Pub/Sub |
| ML Detection | scikit-learn (Isolation Forest) |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker + Docker Compose |
| Orchestration | Kubernetes (manifests in `/k8s`) |
| Language | Python 3.11 |

---

## Services

### Log Ingestion Service (`:8000`)
Receives network log events via HTTP POST. Stores each log in PostgreSQL and publishes it to Redis for downstream processing. Exposes a Prometheus `/metrics` endpoint tracking ingestion throughput.

### Detection Service (`:8001`)
Subscribes to Redis and processes every log through four detection layers:
- **Port Scan** — flags IPs hitting more than 10 unique ports within 10 seconds
- **Brute Force** — flags IPs making 6+ SSH (port 22) attempts within 10 seconds
- **Large Data Transfer** — flags any single transfer exceeding 5,000 bytes
- **ML Anomaly** — Isolation Forest model trained on port, bytes, and request rate features; detects statistical outliers that rule-based logic would miss

When a threat is detected, an alert is written to PostgreSQL with source IP, type, and severity.

### Alert Service (`:8002`)
Read-only API for querying all generated alerts from PostgreSQL.

---

## Getting Started

### Prerequisites
- Docker Desktop
- Docker Compose

### Run the platform

```bash
git clone https://github.com/sanaanidhal/cloud-threat-detection-platform.git
cd cloud-threat-detection-platform
docker compose up --build
```

All 7 containers start automatically: PostgreSQL, Redis, Log Ingestion, Detection Service, Alert Service, Prometheus, and Grafana.

### Send test logs

Open `http://localhost:8000/docs` and POST to `/logs`. Example payload:

```json
{
  "source_ip": "192.168.1.100",
  "destination_ip": "10.0.0.1",
  "port": 22,
  "bytes_sent": 6000,
  "protocol": "TCP"
}
```

Send 6+ requests with port 22 to trigger a brute force alert. Vary the port across 10+ values to trigger a port scan. Use `bytes_sent > 5000` to trigger a large data transfer alert.

### View alerts

```
GET http://localhost:8002/alerts
```

---

## Monitoring Dashboard

Grafana is available at `http://localhost:3000` (login: `admin` / `admin`).

The **Threat Detection Platform** dashboard includes:

| Panel | Query | Description |
|---|---|---|
| Logs Ingested per Minute | `rate(logs_ingested_total[2m])` | Ingestion service throughput |
| Logs Processed per Minute | `rate(logs_processed_total[2m])` | Detection engine throughput |
| Total Alerts | `sum(alerts_triggered_total)` | Cumulative alert count |
| Alerts by Attack Type | `alerts_triggered_total` by `type` | BRUTE_FORCE, PORT_SCAN, ML_ANOMALY, LARGE_DATA_TRANSFER |
| Alerts by Severity | `alerts_triggered_total` by `severity` | HIGH vs MEDIUM distribution |
| Avg Log Processing Time | histogram ratio | Detection engine latency in ms |

Prometheus scrapes both services every 5 seconds at `/metrics`.

---

## Detection Examples

| Scenario | Rule | Severity |
|---|---|---|
| 11 unique ports from one IP in 10s | Port Scan | HIGH |
| 6 SSH attempts from one IP in 10s | Brute Force | HIGH |
| Single transfer > 5,000 bytes | Large Data Transfer | MEDIUM |
| Statistical outlier (Isolation Forest) | ML Anomaly | MEDIUM |

---

## Project Structure

```
cloud-threat-detection-platform/
├── services/
│   ├── log-ingestion/        # FastAPI ingestion service
│   ├── detection-service/    # Threat detection + ML inference
│   └── alert-service/        # Alert query API
├── k8s/                      # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── postgres/
│   ├── redis/
│   ├── log-ingestion/
│   ├── detection-service/
│   └── alert-service/
├── ml/                       # Model training scripts
├── scripts/                  # Log generator
├── docker-compose.yml
├── prometheus.yml
└── init.sql
```

---

## Kubernetes

Production-ready Kubernetes manifests are in `/k8s`. Each service has a `Deployment` and `Service` manifest. Key features:

- **Namespace isolation** — all resources in `threat-detection` namespace
- **ConfigMap** — non-sensitive config (Redis host, ports, DB name)
- **Secret** — sensitive values (DB password, connection string)
- **Readiness probes** — traffic only routes to healthy pods
- **Resource limits** — CPU and memory bounds on every container
- **Horizontal scaling** — log-ingestion runs 2 replicas by default
- **LoadBalancer services** — log-ingestion and alert-service exposed externally

Designed for deployment on AWS EKS. Apply with:

```bash
kubectl apply -f k8s/
```

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `DATABASE_URL` | ingestion, detection, alert | PostgreSQL connection string |
| `REDIS_HOST` | ingestion, detection | Redis hostname |
| `REDIS_PORT` | ingestion, detection | Redis port (default 6379) |

---

## Roadmap

- [x] Log ingestion service
- [x] Redis Pub/Sub event streaming
- [x] Rule-based threat detection
- [x] ML anomaly detection (Isolation Forest)
- [x] Alert service
- [x] Docker Compose orchestration
- [x] Prometheus metrics + Grafana dashboard
- [x] Kubernetes manifests
- [ ] AWS EKS deployment
- [x] CI/CD pipeline (GitHub Actions)
