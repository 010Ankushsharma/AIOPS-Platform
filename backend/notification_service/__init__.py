"""Notification Service - Multi-channel alert delivery."""
import httpx
from enum import Enum
from dataclasses import dataclass
from backend.shared.config import get_settings
import structlog

settings = get_settings()
logger = structlog.get_logger()


class NotificationChannel(str, Enum):
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"
    WEBHOOK = "webhook"


@dataclass
class NotificationPayload:
    title: str
    message: str
    severity: str
    incident_id: str = ""
    channel: NotificationChannel = NotificationChannel.SLACK
    metadata: dict = None


class NotificationService:
    """Delivers notifications across multiple channels."""

    async def send(self, payload: NotificationPayload):
        """Route notification to appropriate channel."""
        handlers = {
            NotificationChannel.SLACK: self._send_slack,
            NotificationChannel.TEAMS: self._send_teams,
            NotificationChannel.EMAIL: self._send_email,
            NotificationChannel.WEBHOOK: self._send_webhook,
        }
        handler = handlers.get(payload.channel, self._send_slack)
        await handler(payload)

    async def _send_slack(self, payload: NotificationPayload):
        """Send Slack notification via webhook."""
        if not settings.SLACK_WEBHOOK_URL:
            logger.warning("Slack webhook not configured")
            return

        color_map = {"P0": "#FF0000", "P1": "#FF6600", "P2": "#FFAA00", "P3": "#00AA00"}
        
        slack_body = {
            "attachments": [{
                "color": color_map.get(payload.severity, "#808080"),
                "title": f"🚨 {payload.title}",
                "text": payload.message,
                "fields": [
                    {"title": "Severity", "value": payload.severity, "short": True},
                    {"title": "Incident", "value": payload.incident_id, "short": True},
                ],
                "footer": "AIOps Platform",
            }]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(settings.SLACK_WEBHOOK_URL, json=slack_body)

    async def _send_teams(self, payload: NotificationPayload):
        """Send Microsoft Teams notification."""
        if not settings.TEAMS_WEBHOOK_URL:
            return
        
        teams_body = {
            "@type": "MessageCard",
            "summary": payload.title,
            "themeColor": "FF0000" if payload.severity == "P0" else "FF6600",
            "title": f"🚨 {payload.title}",
            "sections": [{
                "text": payload.message,
                "facts": [
                    {"name": "Severity", "value": payload.severity},
                    {"name": "Incident", "value": payload.incident_id},
                ],
            }],
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(settings.TEAMS_WEBHOOK_URL, json=teams_body)

    async def _send_email(self, payload: NotificationPayload):
        """Send email notification."""
        # In production: use aiosmtplib
        logger.info("Email notification", title=payload.title)

    async def _send_webhook(self, payload: NotificationPayload):
        """Send generic webhook notification."""
        logger.info("Webhook notification", title=payload.title)
