import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model.pkl")

model = joblib.load(MODEL_PATH)

def predict_anomaly(port, bytes_sent, request_rate):

    features = [[
        port,
        bytes_sent,
        request_rate
    ]]

    prediction = model.predict(features)

    return prediction[0] == -1