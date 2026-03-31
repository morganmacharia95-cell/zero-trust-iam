import pytest
from unittest.mock import MagicMock
from app.core.policy_evaluator import evaluate_policy
from app.models.models import Policy


def make_policy(**kwargs) -> Policy:
    defaults = dict(
        name="test-policy",
        role="analyst",
        resource="finance-reports",
        action="READ",
        effect="ALLOW",
        allowed_hours_start=None,
        allowed_hours_end=None,
        allowed_ip_range=None,
        max_risk_score=60,
    )
    defaults.update(kwargs)
    p = Policy(**defaults)
    return p


def mock_db(policies: list):
    db = MagicMock()
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.all.return_value = policies
    db.query.return_value = query_mock
    return db


# ── Basic ALLOW / DENY ─────────────────────────────────────
def test_allow_matching_policy():
    db = mock_db([make_policy(effect="ALLOW")])
    decision, reason = evaluate_policy(db, "analyst", "finance-reports", "READ", risk_score=10)
    assert decision == "ALLOW"


def test_deny_explicit_deny_rule():
    db = mock_db([make_policy(effect="DENY")])
    decision, reason = evaluate_policy(db, "analyst", "finance-reports", "WRITE", risk_score=10)
    assert decision == "DENY"


def test_deny_no_policy():
    db = mock_db([])
    decision, reason = evaluate_policy(db, "analyst", "prod-database", "DELETE", risk_score=10)
    assert decision == "DENY"
    assert "No policy found" in reason


# ── Risk score checks ──────────────────────────────────────
def test_deny_when_risk_score_exceeds_max():
    db = mock_db([make_policy(effect="ALLOW", max_risk_score=40)])
    decision, reason = evaluate_policy(db, "analyst", "finance-reports", "READ", risk_score=75)
    assert decision == "DENY"
    assert "Risk score" in reason


def test_allow_when_risk_score_within_limit():
    db = mock_db([make_policy(effect="ALLOW", max_risk_score=60)])
    decision, reason = evaluate_policy(db, "analyst", "finance-reports", "READ", risk_score=30)
    assert decision == "ALLOW"


# ── Time-of-day checks ────────────────────────────────────
def test_deny_outside_allowed_hours():
    from unittest.mock import patch
    from datetime import datetime, timezone
    # Mock 3am UTC
    fake_now = datetime(2024, 6, 15, 3, 0, 0, tzinfo=timezone.utc)
    with patch("app.core.policy_evaluator.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        db = mock_db([make_policy(effect="ALLOW", allowed_hours_start=8, allowed_hours_end=18)])
        decision, reason = evaluate_policy(db, "analyst", "finance-reports", "READ", risk_score=10)
    assert decision == "DENY"
    assert "hours" in reason


def test_allow_within_allowed_hours():
    from unittest.mock import patch
    from datetime import datetime, timezone
    fake_now = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    with patch("app.core.policy_evaluator.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        db = mock_db([make_policy(effect="ALLOW", allowed_hours_start=8, allowed_hours_end=18)])
        decision, reason = evaluate_policy(db, "analyst", "finance-reports", "READ", risk_score=10)
    assert decision == "ALLOW"
