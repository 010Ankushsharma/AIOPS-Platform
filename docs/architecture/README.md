# Architecture Guide

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                              │
│     Next.js Dashboard │ CLI │ Slack Bot │ External Integrations                  │
└────────────────────────────────┬─────────────────────────────────────────────────┘
                                 │ HTTPS/WSS
┌────────────────────────────────▼─────────────────────────────────────────────────┐
│                          API GATEWAY (FastAPI)                                    │
│  ┌──────────┐ ┌─────────────┐ ┌──────────────┐ ┌───────────┐ ┌──────────────┐  │
│  │   Auth   │ │ Rate Limit  │ │   Routing    │ │ Versioning│ │  Validation  │  │
│  └──────────┘ └─────────────┘ └──────────────┘ └───────────┘ └──────────────┘  │
└────────────────────────────────┬─────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────┼─────────────────────────────────────────────────┐
│                     MESSAGE BUS (RabbitMQ)                                        │
└──┬──────────┬──────────┬───────┼──────────┬──────────┬──────────┬───────────────┘
   │          │          │       │          │          │          │
┌──▼──┐  ┌───▼──┐  ┌───▼───┐ ┌─▼──┐  ┌───▼───┐  ┌──▼──┐  ┌──▼──────────┐
│ Log │  │Metric│  │ Event │ │Anom│  │  RCA  │  │ KG  │  │     AI      │
│Coll.│  │Coll. │  │Correl.│ │Det.│  │Engine │  │Svc. │  │  Reasoning  │
└──┬──┘  └───┬──┘  └───┬───┘ └─┬──┘  └───┬───┘  └──┬──┘  │  (LangGraph)│
   │          │          │       │          │          │     └──┬──────────┘
   └──────────┴──────────┴───────┴──────────┴──────────┴────────┘
                                 │
┌────────────────────────────────┼─────────────────────────────────────────────────┐
│                        DATA LAYER                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │PostgreSQL│ │  Redis   │ │  Neo4j   │ │  Qdrant  │ │  MinIO   │              │
│  │(Primary) │ │ (Cache)  │ │ (Graph)  │ │ (Vector) │ │(Storage) │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
└──────────────────────────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────┼─────────────────────────────────────────────────┐
│                     OBSERVABILITY                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐                       │
│  │Prometheus│ │ Grafana  │ │   Loki   │ │OpenTelemetry │                       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘                       │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Ingestion** → Logs/metrics arrive via REST API or message queue
2. **Normalization** → Data is parsed, enriched, and tagged
3. **Storage** → PostgreSQL (structured), Qdrant (embeddings), Neo4j (relationships)
4. **Detection** → Anomaly detection runs on incoming data streams
5. **Correlation** → Related alerts are grouped into incidents
6. **Investigation** → LangGraph agents analyze the incident
7. **Remediation** → Fix suggestions generated, optionally as PRs
8. **Notification** → Teams alerted via Slack/Teams/Email

## Design Principles

- **Event-Driven**: All services communicate via RabbitMQ events
- **Hexagonal Architecture**: Core logic isolated from infrastructure
- **Domain-Driven Design**: Bounded contexts per service
- **CQRS**: Read/write separation for high-throughput data
- **Circuit Breaker**: Resilient inter-service communication

## Security Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Client    │────▶│  API Gateway │────▶│   Service      │
│             │     │  (JWT Valid) │     │  (RBAC Check)  │
└─────────────┘     └──────────────┘     └────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Audit Log  │
                    └─────────────┘
```

- JWT tokens with short expiry (60 min)
- Role-based access (Admin, SRE, DevOps, Developer, Auditor)
- All actions audit-logged
- Secrets in Kubernetes Secrets / Vault
- Network policies for pod-to-pod communication
