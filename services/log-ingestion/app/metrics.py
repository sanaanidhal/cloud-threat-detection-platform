from prometheus_client import Counter

logs_ingested = Counter(
    "logs_ingested_total",
    "Total number of logs received by the ingestion service"
)