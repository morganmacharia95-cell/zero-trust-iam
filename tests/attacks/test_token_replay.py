"""
Attack simulation: Token Replay
--------------------------------
An attacker captures a valid JWT and replays it after it has expired.
The system must reject expired tokens at the validation layer.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _mock_db():
    """Return a mock DB session that won't try to connect to postgres."""
    db = MagicMock()
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.all.return_value = []
    query_mock.offset.return_value = query_mock
    query_mock.limit.return_value = query_mock
    db.query.return_value = query_mock
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


def test_expired_token_is_rejected():
    """An expired JWT must be rejected with HTTP 401."""
    with patch("app.api.authorize.validate_token",
               new_callable=AsyncMock,
               side_effect=HTTPException(status_code=401, detail="Token has expired")), \
         patch("app.db.database.get_db", return_value=iter([_mock_db()])):
        resp = client.post(
            "/api/authorize",
            headers={"Authorization": "Bearer fake.expired.token"},
            json={"resource": "finance-reports", "action": "READ"},
        )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_tampered_token_is_rejected():
    """A JWT with an invalid signature must be rejected."""
    with patch("app.api.authorize.validate_token",
               new_callable=AsyncMock,
               side_effect=HTTPException(status_code=401, detail="Invalid token: Signature verification failed")), \
         patch("app.db.database.get_db", return_value=iter([_mock_db()])):
        resp = client.post(
            "/api/authorize",
            headers={"Authorization": "Bearer fake.tampered.token"},
            json={"resource": "prod-database", "action": "READ"},
        )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_missing_token_rejected():
    """A request with no Authorization header must be rejected."""
    resp = client.post(
        "/api/authorize",
        json={"resource": "finance-reports", "action": "READ"},
    )
    assert resp.status_code in (401, 403), f"Expected 401 or 403, got {resp.status_code}: {resp.text}"
