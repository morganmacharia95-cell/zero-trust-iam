from datetime import datetime, timezone
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()

# Cache JWKS in memory (refreshed on each process start)
_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        # Use internal Docker hostname for container-to-container communication
        jwks_url = settings.keycloak_jwks_url.replace(
            "http://localhost:8080", "http://keycloak:8080"
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache


async def validate_token(token: str) -> dict:
    try:
        jwks = await _get_jwks()
        # Accept tokens issued by either hostname
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={
                "verify_exp": True,
                "verify_aud": False,  # skip audience check for now
            },
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Manually verify issuer — accept both localhost and keycloak hostnames
    issuer = payload.get("iss", "")
    if "zero-trust-demo" not in issuer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: Invalid issuer {issuer}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def extract_user_info(payload: dict) -> dict:
    """
    Pulls standard fields from a decoded Keycloak JWT payload.
    Returns a clean dict used by the policy evaluator.
    """
    realm_roles = payload.get("realm_access", {}).get("roles", [])
    # Pick the most privileged project role present
    role = "anonymous"
    for r in ["admin", "engineer", "analyst"]:
        if r in realm_roles:
            role = r
            break

    return {
        "user_id": payload.get("sub", ""),
        "username": payload.get("preferred_username", ""),
        "email": payload.get("email", ""),
        "role": role,
        "roles": realm_roles,
        "token_exp": payload.get("exp"),
    }
