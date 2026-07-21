"""Integration tests for API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.api_gateway.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    """Get auth headers for testing."""
    from backend.shared.security import create_access_token
    token = create_access_token(user_id="test-user", role="admin")
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_login_success(self, client):
        response = await client.post("/api/v1/auth/login", json={
            "email": "admin@aiops.dev",
            "password": "admin"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_failure(self, client):
        response = await client.post("/api/v1/auth/login", json={
            "email": "wrong@email.com",
            "password": "wrong"
        })
        assert response.status_code == 401


class TestIncidentEndpoints:
    @pytest.mark.asyncio
    async def test_create_incident(self, client, auth_headers):
        response = await client.post("/api/v1/incidents", json={
            "title": "Test incident for integration test",
            "severity": "P2",
            "tags": ["test"]
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test incident for integration test"
        assert data["severity"] == "P2"

    @pytest.mark.asyncio
    async def test_list_incidents(self, client, auth_headers):
        response = await client.get("/api/v1/incidents", headers=auth_headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_analyze_incident(self, client, auth_headers):
        response = await client.post("/api/v1/incidents/analyze", json={
            "incident_id": "00000000-0000-0000-0000-000000000001",
            "include_logs": True,
            "include_metrics": True,
            "time_window_minutes": 60
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "root_cause" in data
        assert "confidence" in data
        assert data["confidence"] > 0


class TestLogEndpoints:
    @pytest.mark.asyncio
    async def test_ingest_logs(self, client, auth_headers):
        response = await client.post("/api/v1/logs", json={
            "logs": [{
                "service": "test-service",
                "timestamp": "2026-06-10T10:00:00Z",
                "level": "ERROR",
                "message": "Connection refused",
                "host": "node-1"
            }]
        }, headers=auth_headers)
        assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_ingest_logs_unauthorized(self, client):
        response = await client.post("/api/v1/logs", json={
            "logs": [{"service": "x", "timestamp": "2026-06-10T10:00:00Z", "level": "INFO", "message": "hi"}]
        })
        assert response.status_code == 403


class TestMetricsEndpoints:
    @pytest.mark.asyncio
    async def test_ingest_metrics(self, client, auth_headers):
        response = await client.post("/api/v1/metrics", json={
            "metrics": [{
                "service": "payment-service",
                "metric_name": "cpu_percent",
                "value": 75.5,
                "timestamp": "2026-06-10T10:00:00Z",
                "host": "node-1"
            }]
        }, headers=auth_headers)
        assert response.status_code == 202
