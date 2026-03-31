#!/usr/bin/env python3
"""
CLI helper — gets a JWT access token from Keycloak for a test user.

Usage:
    python get_token.py analyst_bob
    python get_token.py engineer_alice
    python get_token.py admin_user
"""

import sys
import httpx
import json

KEYCLOAK_URL = "http://localhost:8080"
REALM        = "zero-trust-demo"
CLIENT_ID    = "policy-engine"
CLIENT_SECRET = "policy-engine-secret"

USERS = {
    "admin_user":     "Admin@123!",
    "engineer_alice": "Engineer@123!",
    "analyst_bob":    "Analyst@123!",
}

def get_token(username: str) -> str:
    password = USERS.get(username)
    if not password:
        print(f"Unknown user: {username}")
        print(f"Available users: {list(USERS.keys())}")
        sys.exit(1)

    url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    resp = httpx.post(url, data={
        "grant_type":    "password",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username":      username,
        "password":      password,
        "scope":         "openid",
    })

    if resp.status_code != 200:
        print(f"Error: {resp.status_code} — {resp.text}")
        sys.exit(1)

    data = resp.json()
    return data["access_token"]


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "analyst_bob"
    token = get_token(username)
    print(f"\nToken for {username}:\n")
    print(token)
    print(f"\n\nUse it like this:\n")
    print(f'curl -X POST http://localhost:8000/api/authorize \\')
    print(f'  -H "Authorization: Bearer {token[:40]}..." \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"resource": "finance-reports", "action": "READ"}}\'')
