# Zero Trust IAM — Developer Shortcuts
# Usage: make <target>

.PHONY: help up down logs ps build test test-unit test-attacks \
        token-analyst token-engineer token-admin shell-policy shell-db

help:
	@echo ""
	@echo "  Zero Trust IAM — available commands"
	@echo ""
	@echo "  make up              Start all services"
	@echo "  make down            Stop all services"
	@echo "  make build           Rebuild all Docker images"
	@echo "  make logs            Tail all service logs"
	@echo "  make ps              Show running containers"
	@echo ""
	@echo "  make test            Run all tests"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make test-attacks    Run attack simulation tests"
	@echo ""
	@echo "  make token-analyst   Print a JWT for analyst_bob"
	@echo "  make token-engineer  Print a JWT for engineer_alice"
	@echo "  make token-admin     Print a JWT for admin_user"
	@echo ""
	@echo "  make shell-policy    Open bash shell in policy-engine container"
	@echo "  make shell-db        Open psql in postgres container"
	@echo ""

# ── Docker ────────────────────────────────────────────────
up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up -d
	@echo "Services starting... check status with: make ps"
	@echo "Policy engine: http://localhost:8000/docs"
	@echo "Keycloak:      http://localhost:8080"
	@echo "Dashboard:     http://localhost:3000"

down:
	docker compose down

build:
	docker compose build --no-cache

logs:
	docker compose logs -f

ps:
	docker compose ps

# ── Testing ───────────────────────────────────────────────
test:
	cd policy-engine && \
	  pip install -q pytest pytest-asyncio pytest-cov && \
	  pytest ../tests -v --cov=app --cov-report=term-missing

test-unit:
	cd policy-engine && pytest ../tests/unit -v

test-attacks:
	cd policy-engine && pytest ../tests/attacks -v

# ── Token helpers ─────────────────────────────────────────
token-analyst:
	python3 keycloak/scripts/get_token.py analyst_bob

token-engineer:
	python3 keycloak/scripts/get_token.py engineer_alice

token-admin:
	python3 keycloak/scripts/get_token.py admin_user

# ── Shell access ──────────────────────────────────────────
shell-policy:
	docker compose exec policy-engine bash

shell-db:
	docker compose exec postgres psql -U ztiam -d zero_trust
