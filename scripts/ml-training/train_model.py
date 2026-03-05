import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

np.random.seed(42)

# ------------------------
# NORMAL TRAFFIC
# ------------------------

normal_samples = 10000

normal_ports = np.random.choice(
    [80, 443, 22, 53],
    normal_samples
)

normal_bytes = np.random.normal(
    loc=800,
    scale=200,
    size=normal_samples
)

normal_requests = np.random.normal(
    loc=5,
    scale=2,
    size=normal_samples
)

# ------------------------
# ANOMALOUS TRAFFIC
# ------------------------

anomaly_samples = 2000

anomaly_ports = np.random.randint(
    1000,
    65000,
    anomaly_samples
)

anomaly_bytes = np.random.normal(
    loc=10000,
    scale=3000,
    size=anomaly_samples
)

anomaly_requests = np.random.normal(
    loc=50,
    scale=10,
    size=anomaly_samples
)

# ------------------------
# COMBINE DATA
# ------------------------

ports = np.concatenate([normal_ports, anomaly_ports])
bytes_sent = np.concatenate([normal_bytes, anomaly_bytes])
request_rate = np.concatenate([normal_requests, anomaly_requests])

data = pd.DataFrame({
    "port": ports,
    "bytes_sent": bytes_sent,
    "request_rate": request_rate
})

print("Dataset shape:", data.shape)

# ------------------------
# TRAIN MODEL
# ------------------------

model = IsolationForest(
    contamination=0.1,
    random_state=42
)

model.fit(data)

# ------------------------
# SAVE MODEL
# ------------------------

output_path = os.path.join(
    "..",
    "..",
    "services",
    "detection-service",
    "model.pkl"
)

joblib.dump(model, output_path)

print("Model saved to:", output_path)