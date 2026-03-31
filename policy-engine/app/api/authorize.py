from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.db.database import get_db
from app.core.jwt_validator import validate_token, extract_user_info
from app.core.policy_evaluator import evaluate_policy
from app.core.audit_logger import log_event
from app.config import get_settings

router = APIRouter()
bearer = HTTPBearer()
settings = get_settings()


# ── Request / Response schemas ────────────────────────────
class AuthorizeRequest(BaseModel):
    resource: str   # e.g. "finance-reports"
    action:   str   # READ | WRITE | DELETE | EXECUTE


class AuthorizeResponse(BaseModel):
    decision:    str          # ALLOW | DENY
    reason:      str
    user_id:     str
    username:    str
    role:        str
    risk_score:  int
    risk_level:  str
    resource:    str
    action:      str


# ── Risk Engine helper ────────────────────────────────────
async def get_risk_score(request: Request, user_info: dict) -> tuple[int, str]:
    """Calls the risk engine and returns (score, level)."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(
                f"{settings.risk_engine_url}/score",
                json={
                    "user_id":    user_info["user_id"],
                    "username":   user_info["username"],
                    "ip_address": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", ""),
                },
            )
            data = resp.json()
            return data.get("score", 0), data.get("level", "LOW")
    except Exception:
        # If risk engine is unreachable, default to moderate risk
        return 30, "MEDIUM"


# ── Main endpoint ─────────────────────────────────────────
@router.post("/authorize", response_model=AuthorizeResponse)
async def authorize(
    body: AuthorizeRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    """
    Core Zero Trust authorization endpoint.

    Flow:
      1. Validate JWT with Keycloak
      2. Extract user identity + role
      3. Get risk score from risk engine
      4. Evaluate RBAC + ABAC policy
      5. Log the decision (always)
      6. Return ALLOW or DENY
    """
    # Step 1 — Validate token
    payload   = await validate_token(credentials.credentials)
    user_info = extract_user_info(payload)

    # Step 2 — Get risk score
    risk_score, risk_level = await get_risk_score(request, user_info)

    # Step 3 — Evaluate policy
    decision, reason = evaluate_policy(
        db=db,
        role=user_info["role"],
        resource=body.resource,
        action=body.action,
        risk_score=risk_score,
        ip_address=request.client.host if request.client else None,
    )

    # Step 4 — Log every decision (audit trail)
    log_event(
        db=db,
        user_id=user_info["user_id"],
        username=user_info["username"],
        user_role=user_info["role"],
        resource=body.resource,
        action=body.action,
        decision=decision,
        deny_reason=reason if decision == "DENY" else None,
        risk_score=risk_score,
        risk_level=risk_level,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        token_exp=user_info.get("token_exp"),
    )

    return AuthorizeResponse(
        decision=decision,
        reason=reason,
        user_id=user_info["user_id"],
        username=user_info["username"],
        role=user_info["role"],
        risk_score=risk_score,
        risk_level=risk_level,
        resource=body.resource,
        action=body.action,
    )
