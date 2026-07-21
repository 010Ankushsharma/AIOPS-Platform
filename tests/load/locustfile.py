"""Load tests using Locust."""
from locust import HttpUser, task, between


class AIOpsLoadTest(HttpUser):
    """Load test for AIOps platform API."""
    
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        """Login and get token."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "admin@aiops.dev",
            "password": "admin"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(10)
    def ingest_logs(self):
        """Simulate high-volume log ingestion."""
        self.client.post("/api/v1/logs", json={
            "logs": [
                {
                    "service": "payment-service",
                    "timestamp": "2026-06-10T10:00:00Z",
                    "level": "ERROR",
                    "message": f"Connection timeout to database",
                    "host": "node-1",
                }
                for _ in range(100)
            ]
        }, headers=self.headers)

    @task(5)
    def ingest_metrics(self):
        """Simulate metric ingestion."""
        self.client.post("/api/v1/metrics", json={
            "metrics": [
                {
                    "service": "payment-service",
                    "metric_name": "cpu_percent",
                    "value": 75.5,
                    "timestamp": "2026-06-10T10:00:00Z",
                }
            ]
        }, headers=self.headers)

    @task(3)
    def list_incidents(self):
        self.client.get("/api/v1/incidents", headers=self.headers)

    @task(1)
    def get_analytics(self):
        self.client.get("/api/v1/analytics", headers=self.headers)

    @task(1)
    def analyze_incident(self):
        self.client.post("/api/v1/incidents/analyze", json={
            "incident_id": "00000000-0000-0000-0000-000000000001",
            "time_window_minutes": 60
        }, headers=self.headers)
