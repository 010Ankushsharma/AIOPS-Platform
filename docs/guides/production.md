# Production Deployment Guide

## Infrastructure Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| API Gateway | 3 pods, 2CPU/2GB | 5 pods, 4CPU/4GB |
| AI Reasoning | 2 pods, 4CPU/8GB | 4 pods, 8CPU/16GB |
| PostgreSQL | 2CPU/8GB, 100GB SSD | 4CPU/16GB, 500GB SSD |
| Redis | 2CPU/4GB | Cluster mode, 3 nodes |
| Neo4j | 2CPU/4GB | 4CPU/8GB |
| Qdrant | 2CPU/4GB | 4CPU/8GB |
| Ollama (GPU) | 1x A10G | 2x A100 |

## Deployment Steps

### 1. Provision Infrastructure

```bash
cd infra/terraform/environments/production
terraform init
terraform plan
terraform apply
```

### 2. Deploy Core Services

```bash
kubectl apply -f infra/kubernetes/base/namespace.yaml
kubectl apply -f infra/kubernetes/base/configmap.yaml
kubectl apply -k infra/kubernetes/overlays/production/
```

### 3. Deploy Monitoring Stack

```bash
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
helm install loki grafana/loki-stack -n monitoring
```

### 4. Deploy Application

```bash
helm install aiops infra/helm/aiops-platform/ -n aiops \
  --set image.tag=$IMAGE_TAG \
  --set environment=production \
  -f infra/helm/aiops-platform/values-production.yaml
```

### 5. Post-Deployment Validation

```bash
# Health checks
curl https://aiops.internal/health

# Run smoke tests
pytest tests/integration/ --env=production --smoke

# Verify monitoring
kubectl port-forward svc/grafana 3001:3000 -n monitoring
```

## Scaling Guidelines

- **100K logs/min**: 5 log collector pods, batch size 2000
- **10K metrics/min**: 3 metrics collector pods
- **PostgreSQL**: Read replicas for analytics queries
- **Redis**: Cluster mode for >50K ops/sec
- **RabbitMQ**: 3-node cluster with quorum queues

## Disaster Recovery

- PostgreSQL: Streaming replication + daily backups to MinIO
- Neo4j: Daily full backup
- Qdrant: Snapshot to object storage
- RTO: 15 minutes, RPO: 5 minutes

## Security Checklist

- [ ] JWT secret rotated
- [ ] Database passwords in K8s Secrets
- [ ] Network policies applied
- [ ] TLS termination at ingress
- [ ] RBAC roles configured
- [ ] Audit logging enabled
- [ ] GitHub App private key secured
- [ ] Rate limiting configured
- [ ] Pod security standards enforced
