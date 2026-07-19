"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ─── Enums ──────────────────────────────────────────────────────────────
class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ─── Log Schemas ────────────────────────────────────────────────────────
class LogIngest(BaseModel):
    service: str = Field(..., min_length=1, max_length=255)
    timestamp: datetime
    level: str = Field(..., pattern="^(ERROR|WARN|INFO|DEBUG|FATAL|TRACE)$")
    message: str = Field(..., min_length=1, max_length=10000)
    source: Optional[str] = None
    host: Optional[str] = None
    container_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    labels: dict = Field(default_factory=dict)


class LogBatchIngest(BaseModel):
    logs: list[LogIngest] = Field(..., min_length=1, max_length=5000)


class LogResponse(BaseModel):
    id: UUID
    service_id: UUID
    timestamp: datetime
    level: str
    message: str
    source: Optional[str]
    host: Optional[str]
    structured_data: dict

    class Config:
        from_attributes = True


# ─── Metric Schemas ─────────────────────────────────────────────────────
class MetricIngest(BaseModel):
    service: str
    metric_name: str = Field(..., min_length=1, max_length=255)
    value: float
    unit: Optional[str] = None
    timestamp: datetime
    labels: dict = Field(default_factory=dict)
    host: Optional[str] = None


class MetricBatchIngest(BaseModel):
    metrics: list[MetricIngest] = Field(..., min_length=1, max_length=2000)


# ─── Incident Schemas ───────────────────────────────────────────────────
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = None
    severity: Severity
    service_id: Optional[UUID] = None
    tags: list[str] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[Severity] = None
    status: Optional[IncidentStatus] = None
    assigned_team_id: Optional[UUID] = None
    assigned_user_id: Optional[UUID] = None
    root_cause: Optional[str] = None


class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    severity: Severity
    status: IncidentStatus
    service_id: Optional[UUID]
    root_cause: Optional[str]
    root_cause_confidence: Optional[float]
    remediation_plan: dict
    timeline: list
    tags: list[str]
    detected_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentAnalyzeRequest(BaseModel):
    incident_id: UUID
    include_logs: bool = True
    include_metrics: bool = True
    include_deployments: bool = True
    time_window_minutes: int = Field(default=60, ge=5, le=1440)


class IncidentAnalyzeResponse(BaseModel):
    incident_id: UUID
    root_cause: str
    confidence: float
    evidence: list[dict]
    affected_services: list[str]
    contributing_factors: list[str]
    remediation_steps: list[dict]
    ai_model: str
    analysis_duration_ms: int


# ─── RCA Schemas ────────────────────────────────────────────────────────
class RCAResponse(BaseModel):
    id: UUID
    incident_id: UUID
    root_cause: str
    confidence: float
    evidence: list[dict]
    affected_services: list[str]
    remediation_steps: list[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── GitHub PR Schemas ──────────────────────────────────────────────────
class PRGenerateRequest(BaseModel):
    incident_id: UUID
    fix_type: str = Field(..., pattern="^(code|config|infrastructure)$")
    target_repo: str
    target_branch: str = "main"
    auto_merge: bool = False


class PRGenerateResponse(BaseModel):
    pr_url: str
    pr_number: int
    title: str
    description: str
    risk_analysis: dict
    confidence: float
    requires_review: bool = True


# ─── Analytics Schemas ──────────────────────────────────────────────────
class AnalyticsResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_incidents: int
    mttr_minutes: float
    mttd_minutes: float
    incidents_by_severity: dict
    incidents_by_service: dict
    ai_accuracy: float
    auto_resolved_count: int


# ─── Alert Schemas ──────────────────────────────────────────────────────
class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: Severity
    source: str
    service: str
    labels: dict = Field(default_factory=dict)


# ─── Auth Schemas ───────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserLogin(BaseModel):
    email: str
    password: str
