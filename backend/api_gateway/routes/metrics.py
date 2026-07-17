"""Metrics ingestion API endpoints."""
from fastapi import APIRouter, Depends, BackgroundTasks
from backend.shared.schemas import MetricBatchIngest
from backend.shared.security import get_current_user
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.post("", status_code=202)
async def ingest_metrics(
    payload: MetricBatchIngest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Ingest a batch of metric datapoints."""
    logger.info("Metrics batch received", count=len(payload.metrics))
    background_tasks.add_task(_process_metrics, payload.metrics)
    return {"accepted": len(payload.metrics), "status": "queued"}


@router.get("/{service_name}")
async def get_metrics(
    service_name: str,
    metric_name: str = None,
    minutes: int = 60,
    user: dict = Depends(get_current_user),
):
    """Retrieve metrics for a service."""
    return {"service": service_name, "metrics": [], "period_minutes": minutes}


async def _process_metrics(metrics):
    """Store metrics and forward to anomaly detection."""
    pass
