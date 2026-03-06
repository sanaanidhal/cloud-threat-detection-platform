CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    source_ip VARCHAR(50),
    destination_ip VARCHAR(50),
    port INTEGER,
    protocol VARCHAR(20),
    bytes_sent INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    source_ip VARCHAR(50),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);