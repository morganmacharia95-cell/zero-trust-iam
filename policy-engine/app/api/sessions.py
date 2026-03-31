from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.db.database import get_db
from app.models.models import Session as SessionModel

router = APIRouter()


class SessionOut(BaseModel):
    id:          str
    user_id:     str
    username:    Optional[str]
    user_role:   Optional[str]
    ip_address:  Optional[str]
    risk_score:  int
    risk_level:  Optional[str]
    started_at:  datetime
    last_active: datetime
    is_active:   bool

    class Config:
        from_attributes = True


@router.get("/sessions", response_model=list[SessionOut])
def get_sessions(
    active_only: bool = Query(default=True),
    limit:       int  = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    """Return active sessions for the dashboard sessions panel."""
    query = db.query(SessionModel)
    if active_only:
        query = query.filter(SessionModel.is_active == True)
    sessions = query.order_by(SessionModel.last_active.desc()).limit(limit).all()
    return [
        SessionOut(
            id=str(s.id),
            user_id=s.user_id,
            username=s.username,
            user_role=s.user_role,
            ip_address=s.ip_address,
            risk_score=s.risk_score or 0,
            risk_level=s.risk_level,
            started_at=s.started_at,
            last_active=s.last_active,
            is_active=s.is_active,
        )
        for s in sessions
    ]
