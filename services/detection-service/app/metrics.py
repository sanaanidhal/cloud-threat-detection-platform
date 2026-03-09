from prometheus_client import Counter, Histogram

logs_processed = Counter(
    "logs_processed_total",
    "Total number of logs processed"
)

alerts_triggered = Counter(
    "alerts_triggered_total",
    "Total alerts generated",
    ["severity", "type"]
)

log_processing_duration = Histogram(
    "log_processing_duration_seconds",
    "Time spent processing each log",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)