from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.core.policy_evaluator import evaluate_policy
from app.models.models import Policy


def _db(policies):
    db = MagicMock()
    q = MagicMock()
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = policies
    db.query.return_value = q
    return db


def _pol(effect="ALLOW", **kw):
    p = Policy()
    p.name = kw.get("name", "t")
    p.role = kw.get("role", "analyst")
    p.resource = kw.get("resource", "finance-reports")
    p.action = kw.get("action", "READ")
    p.effect = effect
    p.allowed_hours_start = kw.get("s", None)
    p.allowed_hours_end = kw.get("e", None)
    p.allowed_ip_range = None
    p.max_risk_score = kw.get("max", 60)
    return p


def test_analyst_cannot_delete_prod_database():
    d, r = evaluate_policy(_db([]), "analyst", "prod-database", "DELETE", 10)
    assert d == "DENY"


def test_analyst_cannot_write_finance_reports():
    d, r = evaluate_policy(_db([_pol("DENY", action="WRITE")]), "analyst", "finance-reports", "WRITE", 10)
    assert d == "DENY"


def test_analyst_cannot_access_user_management():
    d, r = evaluate_policy(_db([]), "analyst", "user-management", "WRITE", 10)
    assert d == "DENY"


def test_high_risk_score_blocks_access():
    d, r = evaluate_policy(_db([_pol("ALLOW", max=40)]), "analyst", "finance-reports", "READ", 85)
    assert d == "DENY"


def test_analyst_can_read_during_hours():
    fake = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    with patch("app.core.policy_evaluator.datetime") as m:
        m.now.return_value = fake
        d, r = evaluate_policy(_db([_pol("ALLOW", s=8, e=18, max=60)]), "analyst", "finance-reports", "READ", 5)
    assert d == "ALLOW"


def test_after_hours_blocked():
    fake = datetime(2024, 6, 15, 3, 0, 0, tzinfo=timezone.utc)
    with patch("app.core.policy_evaluator.datetime") as m:
        m.now.return_value = fake
        d, r = evaluate_policy(_db([_pol("ALLOW", s=8, e=18, max=60)]), "analyst", "finance-reports", "READ", 5)
    assert d == "DENY"
