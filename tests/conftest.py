import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

# ── In-memory SQLite for tests (no real Postgres needed) ──
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    db = TestingSession()
    yield db
    db.close()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Sample decoded JWT payloads ────────────────────────────
@pytest.fixture
def analyst_payload():
    return {
        "sub":                "user-analyst-001",
        "preferred_username": "analyst_bob",
        "email":              "bob@zerotrust.local",
        "exp":                9999999999,
        "iss":                "http://localhost:8080/realms/zero-trust-demo",
        "realm_access":       {"roles": ["analyst"]},
    }


@pytest.fixture
def engineer_payload():
    return {
        "sub":                "user-engineer-002",
        "preferred_username": "engineer_alice",
        "email":              "alice@zerotrust.local",
        "exp":                9999999999,
        "iss":                "http://localhost:8080/realms/zero-trust-demo",
        "realm_access":       {"roles": ["engineer"]},
    }


@pytest.fixture
def admin_payload():
    return {
        "sub":                "user-admin-003",
        "preferred_username": "admin_user",
        "email":              "admin@zerotrust.local",
        "exp":                9999999999,
        "iss":                "http://localhost:8080/realms/zero-trust-demo",
        "realm_access":       {"roles": ["admin"]},
    }


@pytest.fixture
def expired_payload():
    return {
        "sub":                "user-expired-999",
        "preferred_username": "expired_user",
        "exp":                1000000000,  # Way in the past
        "iss":                "http://localhost:8080/realms/zero-trust-demo",
        "realm_access":       {"roles": ["analyst"]},
    }
