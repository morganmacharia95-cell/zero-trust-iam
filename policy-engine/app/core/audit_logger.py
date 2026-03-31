from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import AccessEvent


def log_event(
    db: Session,
    user_id: str,
    username: str,
    user_role: str,
    resource: str,
    action: str,
    decision: str,
    deny_reason: str | None,
    risk_score: int,
    risk_level: str,
    ip_address: str | None,
    user_agent: str | None,
    token_exp: int | None,
    geo_country: str | None = None,
    geo_city: str | None = None,
) -> AccessEvent:
    """
    Writes an immutable audit record for every authorization decision.
    Called by the /authorize endpoint regardless of ALLOW or DENY outcome.
    """
    token_exp_dt = None
    if token_exp:
        token_exp_dt = datetime.fromtimestamp(token_exp, tz=timezone.utc)

    event = AccessEvent(
        user_id=user_id,
        username=username,
        user_role=user_role,
        resource=resource,
        action=action,
        decision=decision,
        deny_reason=deny_reason,
        risk_score=risk_score,
        risk_level=risk_level,
        ip_address=ip_address,
        user_agent=user_agent,
        token_exp=token_exp_dt,
        geo_country=geo_country,
        geo_city=geo_city,
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event
