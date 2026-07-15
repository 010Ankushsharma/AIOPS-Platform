# 🤖 Autonomous AI Operations Engineer (AIOps Platform)

Enterprise-grade AIOps platform for automated incident detection, root-cause analysis,
remediation planning, and autonomous PR generation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          API Gateway (FastAPI)                           │
│              Auth │ Rate Limit │ Routing │ Versioning                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────────┐
        │                        │                            │
┌───────▼───────┐  ┌────────────▼──────────┐  ┌─────────────▼────────────┐
│ Log Collector │  │  Metrics Collector    │  │  Incident Management     │
│   Service     │  │     Service           │  │      Service             │
└───────┬───────┘  └────────────┬──────────┘  └─────────────┬────────────┘
        │                        │                            │
        └────────────┬───────────┘                            │
                     │                                        │
         ┌───────────▼───────────┐                            │
         │  Event Correlation    │                            │
         │      Engine           │                            │
         └───────────┬───────────┘                            │
                     │                                        │
         ┌───────────▼───────────┐     ┌──────────────────────▼──────┐
         │  Anomaly Detection    │     │    AI Reasoning Engine      │
         │      Service          │────▶│    (LangGraph Agents)       │
         └───────────────────────┘     └──────────────┬──────────────┘
                                                      │
                     ┌────────────────────────────────┼──────────────┐
                     │                                │              │
         ┌───────────▼───────┐          ┌─────────────▼────┐  ┌─────▼──────┐
         │   RCA Engine      │          │ GitHub Automation│  │Notification│
         └───────────────────┘          │    Service       │  │  Service   │
                                        └──────────────────┘  └────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI |
| AI Agents | LangGraph |
| LLM | Llama 3.1, Qwen 3, DeepSeek R1 (via Ollama) |
| Knowledge Graph | Neo4j |
| Vector DB | Qdrant |
| Database | PostgreSQL |
| Cache | Redis |
| Message Queue | RabbitMQ |
| Object Storage | MinIO |
| Monitoring | Prometheus, Grafana, Loki, OpenTelemetry |
| Frontend | Next.js, TypeScript, TailwindCSS, ShadCN UI |
| Orchestration | Kubernetes |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/aiops-platform.git
cd aiops-platform

# Start local development environment
docker compose -f infra/docker/docker-compose.yml up -d

# Run backend services
cd backend && pip install -r requirements.txt
uvicorn api_gateway.main:app --reload --port 8000

# Run frontend
cd frontend && npm install && npm run dev
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Authentication, routing, rate limiting |
| Log Collector | 8001 | Log ingestion and normalization |
| Metrics Collector | 8002 | Infrastructure/app metrics |
| Event Correlation | 8003 | Alert merging and correlation |
| Anomaly Detection | 8004 | ML-based anomaly detection |
| RCA Engine | 8005 | Root cause analysis |
| Knowledge Graph | 8006 | Neo4j graph operations |
| AI Reasoning | 8007 | LangGraph agent orchestration |
| GitHub Automation | 8008 | PR generation |
| Incident Management | 8009 | Incident lifecycle |
| Notification | 8010 | Multi-channel alerts |
| Frontend | 3000 | Dashboard UI |

## Documentation

- [Architecture Guide](docs/architecture/README.md)
- [API Reference](docs/api/README.md)
- [Developer Guide](docs/guides/developer.md)
- [Production Deployment](docs/guides/production.md)

## License

MIT
