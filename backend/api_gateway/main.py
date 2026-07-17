"""API Gateway - Main entry point for the AIOps platform."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

from backend.api_gateway.routes import (
    logs_router, metrics_router, incidents_router,
    rca_router, github_router, analytics_router, auth_router
)
from backend.api_gateway.middleware.rate_limiter import RateLimiterMiddleware
from backend.shared.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("Starting AIOps Platform", version=settings.APP_VERSION)
    yield
    logger.info("Shutting down AIOps Platform")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade Autonomous AI Operations Engineer",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://aiops.internal"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=600)


@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    """Add X-Response-Time header."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"
    return response


# Routes
PREFIX = settings.API_PREFIX
app.include_router(auth_router, prefix=f"{PREFIX}/auth", tags=["Authentication"])
app.include_router(logs_router, prefix=f"{PREFIX}/logs", tags=["Logs"])
app.include_router(metrics_router, prefix=f"{PREFIX}/metrics", tags=["Metrics"])
app.include_router(incidents_router, prefix=f"{PREFIX}/incidents", tags=["Incidents"])
app.include_router(rca_router, prefix=f"{PREFIX}/rca", tags=["Root Cause Analysis"])
app.include_router(github_router, prefix=f"{PREFIX}/github", tags=["GitHub Automation"])
app.include_router(analytics_router, prefix=f"{PREFIX}/analytics", tags=["Analytics"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
