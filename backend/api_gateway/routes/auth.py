"""Authentication API endpoints."""
from fastapi import APIRouter, HTTPException, status
from backend.shared.schemas import UserLogin, TokenResponse
from backend.shared.security import verify_password, create_access_token
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    """Authenticate user and return JWT token."""
    # In production: query DB for user, verify password
    # Demo: accept test credentials
    if payload.email == "admin@aiops.dev" and payload.password == "admin":
        token = create_access_token(user_id="admin-001", role="admin")
        return {"access_token": token, "token_type": "bearer", "expires_in": 3600}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired JWT token."""
    return {"detail": "Not implemented"}
