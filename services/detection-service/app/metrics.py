from prometheus_client import Counter

logs_processed = Counter(
    "logs_processed_total",
    "Total number of logs processed"
)

alerts_triggered = Counter(
    "alerts_triggered_total",
    "Total alerts generated",
    ["severity", "type"]
)