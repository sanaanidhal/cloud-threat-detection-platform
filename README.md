# cloud-threat-detection-platform
Cloud-native distributed threat detection platform built with FastAPI microservices, Redis pub/sub, PostgreSQL, Kubernetes, and AWS. Includes real-time anomaly detection using Isolation Forest and Prometheus/Grafana monitoring.

## Architecture (Current Phase)

- Log Ingestion Service (FastAPI + PostgreSQL)
- Detection Service (FastAPI background subscriber)
- Redis Pub/Sub event streaming
