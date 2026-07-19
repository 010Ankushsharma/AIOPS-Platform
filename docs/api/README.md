# API Reference

## Base URL

```
Production: https://aiops.internal/api/v1
Staging:    https://aiops-staging.internal/api/v1
Local:      http://localhost:8000/api/v1
```

## Authentication

All endpoints require JWT Bearer token (except `/auth/login`).

```
Authorization: Bearer <token>
```

## Endpoints

### POST /auth/login
Authenticate and receive JWT token.

**Request:**
```json
{"email": "user@company.com", "password": "****"}
```

**Response:**
```json
{"access_token": "eyJ...", "token_type": "bearer", "expires_in": 3600}
```

---

### POST /logs
Ingest log batch.

**Request:**
```json
{
  "logs": [
    {
      "service": "payment-service",
      "timestamp": "2026-06-10T14:23:00Z",
      "level": "ERROR",
      "message": "Connection refused to db-primary",
      "host": "pod-abc123",
      "labels": {"namespace": "production"}
    }
  ]
}
```

**Response:** `202 Accepted`
```json
{"accepted": 1, "status": "queued"}
```

---

### POST /metrics
Ingest metrics batch.

**Request:**
```json
{
  "metrics": [
    {
      "service": "payment-service",
      "metric_name": "cpu_percent",
      "value": 87.5,
      "timestamp": "2026-06-10T14:23:00Z",
      "labels": {"host": "node-1"}
    }
  ]
}
```

---

### GET /incidents
List incidents with filters.

**Query params:** `status`, `severity`, `limit`, `offset`

---

### POST /incidents
Create new incident.

---

### POST /incidents/analyze
Trigger AI-powered RCA. Requires `sre` or `admin` role.

**Request:**
```json
{
  "incident_id": "uuid",
  "include_logs": true,
  "include_metrics": true,
  "time_window_minutes": 60
}
```

**Response:**
```json
{
  "incident_id": "uuid",
  "root_cause": "Database connection pool exhaustion...",
  "confidence": 0.87,
  "evidence": [...],
  "affected_services": ["payment-service", "order-service"],
  "remediation_steps": [
    {"step": 1, "action": "Rollback to v2.3.0", "risk": "low"}
  ],
  "ai_model": "llama3.1:8b-instruct",
  "analysis_duration_ms": 4520
}
```

---

### POST /github/pr
Generate a Pull Request with AI fix. Requires `sre` or `admin` role.

**Request:**
```json
{
  "incident_id": "uuid",
  "fix_type": "config",
  "target_repo": "org/repo-name",
  "target_branch": "main"
}
```

---

### GET /analytics
Platform KPIs and analytics.

**Query params:** `days` (default: 30)

---

### GET /rca
List RCA reports.

**Query params:** `incident_id`, `min_confidence`, `limit`
