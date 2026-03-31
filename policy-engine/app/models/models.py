import uuid
from datetime import datetime
from sqlalchemy import Column, String, SmallInteger, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name                = Column(String(100), nullable=False)
    role                = Column(String(50),  nullable=False)
    resource            = Column(String(100), nullable=False)
    action              = Column(String(20),  nullable=False)
    effect              = Column(String(10),  nullable=False)
    allowed_hours_start = Column(SmallInteger, nullable=True)
    allowed_hours_end   = Column(SmallInteger, nullable=True)
    allowed_ip_range    = Column(String(50),  nullable=True)
    max_risk_score      = Column(SmallInteger, default=60)
    created_at          = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at          = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AccessEvent(Base):
    __tablename__ = "access_events"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(String(100), nullable=False)
    username     = Column(String(100))
    user_role    = Column(String(50))
    resource     = Column(String(100), nullable=False)
    action       = Column(String(20),  nullable=False)
    decision     = Column(String(10),  nullable=False)
    deny_reason  = Column(String(255))
    risk_score   = Column(SmallInteger, default=0)
    risk_level   = Column(String(10))
    ip_address   = Column(String(45))
    user_agent   = Column(Text)
    geo_country  = Column(String(50))
    geo_city     = Column(String(100))
    token_exp    = Column(DateTime(timezone=True))
    created_at   = Column(DateTime(timezone=True), default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(String(100), nullable=False)
    username    = Column(String(100))
    user_role   = Column(String(50))
    ip_address  = Column(String(45))
    user_agent  = Column(Text)
    risk_score  = Column(SmallInteger, default=0)
    risk_level  = Column(String(10))
    started_at  = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_active = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_active   = Column(Boolean, default=True)
