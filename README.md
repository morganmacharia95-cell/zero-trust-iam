# Zero Trust IAM Simulator

A production-grade Zero Trust Identity & Access Management system built from scratch.
Every access request is verified against identity, context, risk score, and policy —
never trusted by default.

[![CI](https://github.com/YOUR_USERNAME/zero-trust-iam/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/zero-trust-iam/actions)

---

## What this defends against

| Attack | Mechanism | Result |
|---|---|---|
| Stolen JWT replay | Token expiry + signature validation | 401 Rejected |
| Privilege escalation | RBAC policy store | DENY logged |
| After-hours access | ABAC time-of-day rules | DENY logged |
| Credential stuffing | Rate signal (sliding window) | Risk score spike → DENY |
| Lateral movement | Docker network micro-segmentation | Blocked at network layer |
| VPN / Tor access | VPN signal | Risk score elevated |
| Unknown device | Device fingerprint signal | Risk score elevated |

---

## Architecture

```
User + Device
     │
     ▼
Policy Engine (FastAPI)          ← Core authorization service
     │
     ├── JWT Validator           ← Verifies Keycloak tokens (RS256)
     ├── Risk Engine (FastAPI)   ← 5 contextual risk signals
     ├── Policy Evaluator        ← RBAC + ABAC rule engine
     └── Audit Logger            ← Immutable event log (PostgreSQL)

Keycloak                         ← Identity provider (OAuth2 / OIDC)
PostgreSQL                       ← Policy store + audit log
Docker Networks                  ← Micro-segmentation (finance / engineering / admin)
React Dashboard                  ← Live access event visualisation
```

---

## Quick start (Ubuntu 22.04)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/zero-trust-iam.git
cd zero-trust-iam

# 2. Copy env
cp .env.example .env

# 3. Start everything
make up

# 4. Wait ~60s for Keycloak to fully start, then open:
#    Policy Engine API docs → http://localhost:8000/docs
#    Keycloak Admin         → http://localhost:8080  (admin / changeme_admin_password)
#    Dashboard              → http://localhost:3000
```

---

## Test users

| Username | Password | Role |
|---|---|---|
| `admin_user` | `Admin@123!` | admin |
| `engineer_alice` | `Engineer@123!` | engineer |
| `analyst_bob` | `Analyst@123!` | analyst |

---

## Making your first authorization request

```bash
# Step 1 — get a token
python3 keycloak/scripts/get_token.py analyst_bob

# Step 2 — test an ALLOW scenario
curl -X POST http://localhost:8000/api/authorize \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"resource": "finance-reports", "action": "READ"}'

# Step 3 — test a DENY scenario (analyst trying to write)
curl -X POST http://localhost:8000/api/authorize \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"resource": "finance-reports", "action": "WRITE"}'
```

Or open `api-tests.http` in VS Code with the REST Client extension installed.

---

## Running tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Attack simulations
make test-attacks
```

---

## NIST SP 800-207 Alignment

| NIST Principle | Implementation |
|---|---|
| Never trust, always verify | Every request hits /authorize — no implicit trust |
| Least privilege | RBAC policies grant minimum necessary access |
| Assume breach | Immutable audit log + risk scoring on every request |
| Verify explicitly | JWT signature validation + Keycloak JWKS |
| Use all available data | Risk engine: geo, device, time, rate, VPN signals |

---

## Tech stack

- **Policy Engine** — Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **Risk Engine** — Python 3.11, FastAPI (microservice)
- **Identity** — Keycloak 24 (OAuth2, OIDC, TOTP MFA)
- **Micro-segmentation** — Docker isolated networks, Kubernetes NetworkPolicy
- **Dashboard** — React 20, Vite, TypeScript, Recharts
- **Testing** — pytest, pytest-asyncio, locust
- **CI/CD** — GitHub Actions (Ubuntu 22.04 runners)

---

## Project structure

```
zero-trust-iam/
├── policy-engine/      FastAPI authorization service
├── risk-engine/        Contextual risk scoring microservice
├── keycloak/           Realm config + test user scripts
├── infra/              Docker networks + PostgreSQL schema
├── dashboard/          React live access dashboard
├── tests/              Unit, integration + attack simulations
│   └── attacks/        Token replay, privilege escalation, etc.
├── docs/               Security test report + architecture docs
├── Makefile            Developer shortcuts
└── docker-compose.yml  Full stack orchestration
```

---

## Security test report

See [`docs/security-test-report.md`](docs/security-test-report.md) for documented
attack scenarios, detection mechanisms, and evidence of mitigation.
