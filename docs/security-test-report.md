# Security Test Report — Zero Trust IAM Simulator

**Date:** 2024  
**System:** Zero Trust IAM Policy Engine v0.1.0  
**Tester:** [Your Name]  
**Environment:** Docker Compose on Ubuntu 22.04

---

## Summary

| Attack Scenario | Detection Layer | Outcome | Test File |
|---|---|---|---|
| Expired JWT token replay | JWT validator (exp claim) | BLOCKED — HTTP 401 | `tests/attacks/test_token_replay.py` |
| Tampered JWT signature | JWT validator (RS256 JWKS) | BLOCKED — HTTP 401 | `tests/attacks/test_token_replay.py` |
| Missing authorization header | FastAPI HTTP Bearer | BLOCKED — HTTP 403 | `tests/attacks/test_token_replay.py` |
| Analyst → admin escalation | Policy evaluator (RBAC) | DENIED — logged | `tests/attacks/test_privilege_escalation.py` |
| Analyst writes finance data | Policy evaluator (RBAC) | DENIED — logged | `tests/attacks/test_privilege_escalation.py` |
| After-hours access attempt | Policy evaluator (ABAC time) | DENIED — logged | `tests/unit/test_policy_evaluator.py` |
| High risk score request | Policy evaluator (ABAC risk) | DENIED — logged | `tests/unit/test_policy_evaluator.py` |
| Credential stuffing (rate) | Risk engine rate signal | Risk score elevated | `tests/unit/test_risk_scorer.py` |
| Unknown device fingerprint | Risk engine device signal | Risk score elevated | `tests/unit/test_risk_scorer.py` |

---

## Scenario 1 — Expired JWT Token Replay

**Threat:** Attacker captures a valid JWT from network traffic and replays it
after the token has expired.

**Detection mechanism:** The `jwt_validator.py` module decodes the token using
Keycloak's public JWKS endpoint and checks the `exp` (expiry) claim. Tokens
past their expiry timestamp are rejected before reaching the policy engine.

**Evidence:**
```
POST /api/authorize
Authorization: Bearer <expired_token>

Response: 401 Unauthorized
{ "detail": "Token has expired" }
```

**Audit log entry:**
```
No entry — rejected at JWT validation layer before policy evaluation
```

---

## Scenario 2 — Privilege Escalation (Analyst → Admin)

**Threat:** An analyst-role user attempts to access resources scoped to
admin or engineer roles — either by guessing endpoint names or by
replaying a request captured from a higher-privilege session.

**Detection mechanism:** The `policy_evaluator.py` module queries the policy
store for the user's declared role (extracted from the verified JWT). The
`analyst` role has explicit DENY policies on `prod-database READ`,
`finance-reports WRITE`, and `user-management WRITE`. No matching ALLOW
policy exists, so access is denied and an audit event is written.

**Evidence:**
```
POST /api/authorize
Role: analyst
Resource: prod-database
Action: READ

Response: 200 OK
{
  "decision": "DENY",
  "reason": "No policy found for role=analyst resource=prod-database action=READ",
  "risk_score": 5,
  "risk_level": "LOW"
}
```

**Audit log entry written:** Yes — every DENY is persisted to `access_events`.

---

## Scenario 3 — After-Hours Access Attempt

**Threat:** An attacker or compromised credential attempts access during
off-hours when legitimate users would not be active.

**Detection mechanism:** ABAC time-of-day rules in `policy_evaluator.py`
check `allowed_hours_start` and `allowed_hours_end` against current UTC time.
For `analyst` reading `finance-reports`, access is only permitted 08:00–18:00 UTC.

**Evidence:**
```
Request at 03:00 UTC:
POST /api/authorize  (role=analyst, resource=finance-reports, action=READ)

Response:
{
  "decision": "DENY",
  "reason": "Access denied outside allowed hours (8:00–18:00 UTC)"
}
```

---

## Scenario 4 — Credential Stuffing / Brute Force

**Threat:** Attacker makes rapid repeated requests (>20 per minute) using
the same user_id, indicating automated credential stuffing or brute force.

**Detection mechanism:** `rate_signal.py` uses a sliding window counter
per `user_id`. After 20 requests in 60 seconds, the risk score increases
exponentially. High risk scores cause the policy evaluator to deny access
based on the policy's `max_risk_score` threshold.

**Evidence:**
```
25 requests in 60 seconds from user_id=attacker-001

Risk signal: rate=100
Weighted score: CRITICAL (82)
Policy max_risk_score: 40
Decision: DENY (risk score 82 exceeds policy maximum 40)
```

---

## Scenario 5 — Unknown Device Fingerprint

**Threat:** A legitimate user's credentials are stolen and used from an
attacker's machine with a different browser / User-Agent.

**Detection mechanism:** `device_signal.py` hashes the `User-Agent` header
to create a device fingerprint per `user_id`. First login registers the
device. Subsequent logins from a different fingerprint raise the risk score
by 70 points, potentially crossing the DENY threshold.

**Evidence:**
```
First login:  User-Agent=Mozilla/5.0 (X11; Linux)   → device score: 0
Second login: User-Agent=curl/7.68.0                 → device score: 70
Weighted risk contribution: 70 × 0.20 = 14 points added to total score
```

---

## Micro-segmentation validation

**Test:** `analyst_user` container attempts to reach `finance-zone` network
directly, bypassing the policy engine.

**Expected result:** TCP connection refused at network layer.

```bash
# Inside engineering zone container:
curl http://finance-service:8080/data

# Result:
curl: (7) Failed to connect to finance-service port 8080: Network unreachable
```

Docker's `internal: true` network flag ensures no cross-zone traffic without
explicit routing through the policy engine.

---

## Recommendations for production hardening

1. Replace in-memory risk signal stores with Redis for persistence across restarts
2. Add refresh token rotation in Keycloak to limit token lifetime impact
3. Enable Keycloak TOTP MFA for admin role (already configured in realm-export.json)
4. Add rate limiting at the API gateway layer (Nginx / Traefik)
5. Ship audit logs to an external SIEM (ELK Stack) for long-term retention
6. Replace ip-api.com free tier with MaxMind GeoIP for production geo signals
