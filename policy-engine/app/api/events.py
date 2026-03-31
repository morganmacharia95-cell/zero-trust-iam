from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

from app.db.database import get_db
from app.models.models import AccessEvent

router = APIRouter()


class EventOut(BaseModel):
    id:          str
    user_id:     str
    username:    Optional[str]
    user_role:   Optional[str]
    resource:    str
    action:      str
    decision:    str
    deny_reason: Optional[str]
    risk_score:  int
    risk_level:  Optional[str]
    ip_address:  Optional[str]
    created_at:  datetime

    class Config:
        from_attributes = True


@router.get("/events", response_model=list[EventOut])
def get_events(
    limit:    int = Query(default=50, le=200),
    offset:   int = Query(default=0),
    decision: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Returns recent access events, newest first. Filterable by decision."""
    query = db.query(AccessEvent).order_by(AccessEvent.created_at.desc())

    if decision:
        query = query.filter(AccessEvent.decision == decision.upper())

    events = query.offset(offset).limit(limit).all()

    return [
        EventOut(
            id=str(e.id),
            user_id=e.user_id,
            username=e.username,
            user_role=e.user_role,
            resource=e.resource,
            action=e.action,
            decision=e.decision,
            deny_reason=e.deny_reason,
            risk_score=e.risk_score or 0,
            risk_level=e.risk_level,
            ip_address=e.ip_address,
            created_at=e.created_at,
        )
        for e in events
    ]


@router.get("/events/stats")
def get_stats(db: Session = Depends(get_db)):
    """Aggregate metrics for the dashboard stat cards."""
    from sqlalchemy import func

    total  = db.query(func.count(AccessEvent.id)).scalar()
    allows = db.query(func.count(AccessEvent.id)).filter(AccessEvent.decision == "ALLOW").scalar()
    denies = db.query(func.count(AccessEvent.id)).filter(AccessEvent.decision == "DENY").scalar()
    avg_risk = db.query(func.avg(AccessEvent.risk_score)).scalar()

    return {
        "total_requests": total,
        "allowed":        allows,
        "denied":         denies,
        "avg_risk_score": round(float(avg_risk or 0), 1),
        "deny_rate":      round((denies / total * 100) if total else 0, 1),
    }
