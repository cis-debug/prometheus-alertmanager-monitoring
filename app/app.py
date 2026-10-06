from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

# 1. Compteur total de requêtes par endpoint et status
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

# 2. Latence des requêtes
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['endpoint']
)

@app.route("/")
def home():
    start = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start)
    return "OK - Flask Monitoring"

@app.route("/api/data")
def data():
    start = time.time()
    time.sleep(random.uniform(0.1, 0.3))
    REQUEST_COUNT.labels(method='GET', endpoint='/api/data', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/api/data').observe(time.time() - start)
    return {"data": "some data"}

# Endpoint pour simuler une erreur 500 -> va déclencher notre alerte HighErrorRate
@app.route("/api/error")
def error():
    start = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/api/error', status='500').inc()
    REQUEST_LATENCY.labels(endpoint='/api/error').observe(time.time() - start)
    return "Internal Error", 500

# Endpoint lent -> va déclencher HighLatency
@app.route("/api/slow")
def slow():
    start = time.time()
    time.sleep(2)
    REQUEST_COUNT.labels(method='GET', endpoint='/api/slow', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/api/slow').observe(time.time() - start)
    return "Slow response"

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
