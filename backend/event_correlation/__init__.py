"""Event Correlation Engine - Merges and correlates alerts."""
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import structlog

logger = structlog.get_logger()


@dataclass
class CorrelatedIncident:
    """A group of correlated alerts forming a single incident."""
    id: str
    alerts: list[dict] = field(default_factory=list)
    services: set = field(default_factory=set)
    severity: str = "P3"
    first_alert_at: datetime = None
    last_alert_at: datetime = None
    is_cascading: bool = False


class EventCorrelationEngine:
    """Correlates alerts across services to detect unified incidents."""

    def __init__(self, correlation_window_seconds: int = 300):
        self.window = timedelta(seconds=correlation_window_seconds)
        self.active_incidents: dict[str, CorrelatedIncident] = {}
        self.alert_buffer: list[dict] = []

    def ingest_alert(self, alert: dict) -> CorrelatedIncident | None:
        """Process incoming alert and attempt correlation."""
        self.alert_buffer.append(alert)
        
        # Try to correlate with existing incidents
        correlated = self._find_correlation(alert)
        
        if correlated:
            correlated.alerts.append(alert)
            correlated.services.add(alert.get("service", "unknown"))
            correlated.last_alert_at = alert.get("timestamp", datetime.utcnow())
            correlated.severity = self._escalate_severity(correlated)
            
            if len(correlated.services) > 1:
                correlated.is_cascading = True
            
            return correlated
        
        # Create new incident
        incident = CorrelatedIncident(
            id=f"INC-{len(self.active_incidents) + 1:06d}",
            alerts=[alert],
            services={alert.get("service", "unknown")},
            severity=alert.get("severity", "P3"),
            first_alert_at=alert.get("timestamp", datetime.utcnow()),
            last_alert_at=alert.get("timestamp", datetime.utcnow()),
        )
        self.active_incidents[incident.id] = incident
        return incident

    def _find_correlation(self, alert: dict) -> CorrelatedIncident | None:
        """Find if alert correlates with an existing active incident."""
        alert_time = alert.get("timestamp", datetime.utcnow())
        alert_service = alert.get("service", "")
        
        for incident in self.active_incidents.values():
            # Time-based correlation
            if incident.last_alert_at and (alert_time - incident.last_alert_at) < self.window:
                # Same service or dependent service
                if alert_service in incident.services:
                    return incident
                # Check if services are related (simplified)
                if self._services_related(alert_service, incident.services):
                    return incident
        return None

    def _services_related(self, service: str, existing_services: set) -> bool:
        """Check if service is related to existing incident services."""
        # In production: query knowledge graph for dependencies
        return False

    def _escalate_severity(self, incident: CorrelatedIncident) -> str:
        """Escalate severity based on alert count and spread."""
        if len(incident.services) >= 3 or len(incident.alerts) >= 10:
            return "P0"
        elif len(incident.services) >= 2 or len(incident.alerts) >= 5:
            return "P1"
        elif len(incident.alerts) >= 3:
            return "P2"
        return incident.severity

    def get_timeline(self, incident_id: str) -> list[dict]:
        """Get unified timeline for a correlated incident."""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            return []
        
        timeline = sorted(incident.alerts, key=lambda a: a.get("timestamp", datetime.min))
        return [
            {
                "timestamp": a.get("timestamp"),
                "service": a.get("service"),
                "title": a.get("title"),
                "severity": a.get("severity"),
            }
            for a in timeline
        ]
