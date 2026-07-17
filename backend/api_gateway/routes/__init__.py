"""API route modules."""
from backend.api_gateway.routes.logs import router as logs_router
from backend.api_gateway.routes.metrics import router as metrics_router
from backend.api_gateway.routes.incidents import router as incidents_router
from backend.api_gateway.routes.rca import router as rca_router
from backend.api_gateway.routes.github import router as github_router
from backend.api_gateway.routes.analytics import router as analytics_router
from backend.api_gateway.routes.auth import router as auth_router

__all__ = [
    "logs_router", "metrics_router", "incidents_router",
    "rca_router", "github_router", "analytics_router", "auth_router"
]
