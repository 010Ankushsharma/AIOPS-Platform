"""SQLAlchemy ORM models for the AIOps platform."""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean,
    DateTime, ForeignKey, JSON, Index, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from backend.shared.database import Base


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


class UserRole(str, Enum):
    ADMIN = "admin"
    SRE = "sre"
    DEVOPS = "devops"
    DEVELOPER = "developer"
    AUDITOR = "auditor"


# ─── Users & Auth ───────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SAEnum(UserRole), default=UserRole.DEVELOPER)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    slack_channel = Column(String(255))
    escalation_policy = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Services & Infrastructure ──────────────────────────────────────────
class Service(Base):
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    repository_url = Column(String(500))
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    tier = Column(Integer, default=3)  # 1=critical, 2=important, 3=standard
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Incidents ──────────────────────────────────────────────────────────
class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_status_severity", "status", "severity"),
        Index("ix_incidents_created", "created_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(SAEnum(Severity), nullable=False)
    status = Column(SAEnum(IncidentStatus), default=IncidentStatus.OPEN)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    assigned_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    root_cause = Column(Text)
    root_cause_confidence = Column(Float)
    remediation_plan = Column(JSONB, default={})
    impact_analysis = Column(JSONB, default={})
    timeline = Column(JSONB, default=[])
    tags = Column(ARRAY(String), default=[])
    detected_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    mitigated_at = Column(DateTime)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rca_reports = relationship("RCAReport", back_populates="incident")


# ─── Logs ───────────────────────────────────────────────────────────────
class LogEntry(Base):
    __tablename__ = "log_entries"
    __table_args__ = (
        Index("ix_logs_service_timestamp", "service_id", "timestamp"),
        Index("ix_logs_level", "level"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    level = Column(String(20), nullable=False)  # ERROR, WARN, INFO, DEBUG
    message = Column(Text, nullable=False)
    source = Column(String(255))
    host = Column(String(255))
    container_id = Column(String(100))
    trace_id = Column(String(64))
    span_id = Column(String(32))
    structured_data = Column(JSONB, default={})
    labels = Column(JSONB, default={})


# ─── Metrics ────────────────────────────────────────────────────────────
class MetricDatapoint(Base):
    __tablename__ = "metric_datapoints"
    __table_args__ = (
        Index("ix_metrics_service_name_ts", "service_id", "metric_name", "timestamp"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    timestamp = Column(DateTime, nullable=False)
    labels = Column(JSONB, default={})
    host = Column(String(255))


# ─── Alerts ─────────────────────────────────────────────────────────────
class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(SAEnum(Severity), nullable=False)
    source = Column(String(255))  # prometheus, custom, anomaly_detection
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    fired_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime)
    labels = Column(JSONB, default={})
    annotations = Column(JSONB, default={})


# ─── RCA Reports ────────────────────────────────────────────────────────
class RCAReport(Base):
    __tablename__ = "rca_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    root_cause = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    evidence = Column(JSONB, default=[])
    affected_services = Column(ARRAY(String), default=[])
    contributing_factors = Column(JSONB, default=[])
    remediation_steps = Column(JSONB, default=[])
    ai_model_used = Column(String(100))
    analysis_duration_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    incident = relationship("Incident", back_populates="rca_reports")


# ─── Deployments ────────────────────────────────────────────────────────
class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    version = Column(String(100), nullable=False)
    commit_sha = Column(String(64))
    deployed_by = Column(String(255))
    environment = Column(String(50))
    status = Column(String(50))  # success, failed, rolling_back
    changelog = Column(Text)
    config_changes = Column(JSONB, default={})
    deployed_at = Column(DateTime, default=datetime.utcnow)


# ─── Audit Log ──────────────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(100))
    details = Column(JSONB, default={})
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
