from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.models.models import Policy

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────
class PolicyCreate(BaseModel):
    name:                str
    role:                str
    resource:            str
    action:              str
    effect:              str
    allowed_hours_start: Optional[int] = None
    allowed_hours_end:   Optional[int] = None
    allowed_ip_range:    Optional[str] = None
    max_risk_score:      int = 60


class PolicyOut(BaseModel):
    id:                  str
    name:                str
    role:                str
    resource:            str
    action:              str
    effect:              str
    allowed_hours_start: Optional[int]
    allowed_hours_end:   Optional[int]
    allowed_ip_range:    Optional[str]
    max_risk_score:      int
    created_at:          datetime

    class Config:
        from_attributes = True


# ── Routes ────────────────────────────────────────────────
@router.get("/policies", response_model=list[PolicyOut])
def list_policies(
    role:     Optional[str] = None,
    resource: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all policies. Optionally filter by role or resource."""
    query = db.query(Policy)
    if role:
        query = query.filter(Policy.role == role)
    if resource:
        query = query.filter(Policy.resource == resource)
    policies = query.order_by(Policy.role, Policy.resource).all()
    return [
        PolicyOut(
            id=str(p.id),
            name=p.name,
            role=p.role,
            resource=p.resource,
            action=p.action,
            effect=p.effect,
            allowed_hours_start=p.allowed_hours_start,
            allowed_hours_end=p.allowed_hours_end,
            allowed_ip_range=p.allowed_ip_range,
            max_risk_score=p.max_risk_score,
            created_at=p.created_at,
        )
        for p in policies
    ]


@router.post("/policies", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy(body: PolicyCreate, db: Session = Depends(get_db)):
    """Create a new access policy rule."""
    if body.effect not in ("ALLOW", "DENY"):
        raise HTTPException(status_code=400, detail="effect must be ALLOW or DENY")
    if body.action not in ("READ", "WRITE", "DELETE", "EXECUTE"):
        raise HTTPException(status_code=400, detail="action must be READ, WRITE, DELETE or EXECUTE")

    policy = Policy(**body.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return PolicyOut(
        id=str(policy.id),
        name=policy.name,
        role=policy.role,
        resource=policy.resource,
        action=policy.action,
        effect=policy.effect,
        allowed_hours_start=policy.allowed_hours_start,
        allowed_hours_end=policy.allowed_hours_end,
        allowed_ip_range=policy.allowed_ip_range,
        max_risk_score=policy.max_risk_score,
        created_at=policy.created_at,
    )


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: str, db: Session = Depends(get_db)):
    """Delete a policy rule by ID."""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()
