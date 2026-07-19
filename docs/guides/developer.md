# Developer Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- kubectl (for K8s deployment)

## Local Development Setup

### 1. Start Infrastructure

```bash
cd infra/docker
docker compose up -d postgres redis rabbitmq neo4j qdrant minio ollama
```

### 2. Pull LLM Model

```bash
docker exec -it aiops-platform-ollama-1 ollama pull llama3.1:8b-instruct-q4_K_M
```

### 3. Backend

```bash
cd backend
pip install poetry
poetry install

# Run migrations
alembic upgrade head

# Start API
uvicorn api_gateway.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Access Services

| Service | URL |
|---------|-----|
| API Docs | http://localhost:8000/api/docs |
| Frontend | http://localhost:3000 |
| Grafana | http://localhost:3001 |
| Neo4j Browser | http://localhost:7474 |
| RabbitMQ UI | http://localhost:15672 |
| MinIO Console | http://localhost:9001 |

## Running Tests

```bash
# Unit tests
pytest tests/unit/ -v --cov=backend --cov-report=term-missing

# Integration tests
pytest tests/integration/ -v

# Load tests
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## Project Structure

```
aiops-platform/
├── backend/
│   ├── api_gateway/          # FastAPI app, routes, middleware
│   ├── log_collector/        # Log ingestion and parsing
│   ├── metrics_collector/    # Metrics ingestion
│   ├── event_correlation/    # Alert correlation engine
│   ├── anomaly_detection/    # Statistical + ML detection
│   ├── rca_engine/           # Root cause analysis
│   ├── knowledge_graph/      # Neo4j operations
│   ├── ai_reasoning/         # LangGraph agents
│   │   ├── agents/           # Individual AI agents
│   │   └── workflows/        # LangGraph workflows
│   ├── github_automation/    # PR generation
│   ├── incident_management/  # Incident lifecycle
│   ├── notification_service/ # Multi-channel notifications
│   └── shared/               # Shared modules
│       ├── config/           # Settings
│       ├── database/         # DB sessions
│       ├── models/           # SQLAlchemy models
│       ├── schemas/          # Pydantic schemas
│       └── security/         # JWT, RBAC
├── frontend/                 # Next.js dashboard
├── infra/
│   ├── docker/              # Dockerfiles & Compose
│   ├── kubernetes/          # K8s manifests
│   ├── helm/                # Helm charts
│   └── terraform/           # IaC
├── monitoring/              # Prometheus, Grafana, Loki configs
├── tests/                   # Unit, integration, load, chaos
├── docs/                    # Documentation
└── .github/workflows/       # CI/CD pipelines
```

## Adding a New Agent

1. Create `backend/ai_reasoning/agents/my_agent.py`
2. Extend `BaseAgent` class
3. Implement `execute(context) -> context` method
4. Register in `CoordinatorAgent`
5. Add to LangGraph workflow if needed
6. Write tests in `tests/unit/test_agents/`

## API Development

1. Define schema in `backend/shared/schemas/__init__.py`
2. Create route in `backend/api_gateway/routes/`
3. Register router in `backend/api_gateway/routes/__init__.py`
4. Write integration tests
5. Update API documentation

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```
