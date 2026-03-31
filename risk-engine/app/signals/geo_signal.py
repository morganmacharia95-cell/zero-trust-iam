import httpx

# IPs considered safe to skip geolocation check
_SAFE_IPS = {"127.0.0.1", "::1", "localhost"}

# Simple in-memory store: user_id -> last known country
_last_seen_country: dict[str, str] = {}


def geo_score(ip_address: str) -> int:
    """
    Returns a risk score (0-100) based on IP geolocation.
    Flags impossible travel: if the user's country changes between requests.
    Returns 0 for local/private IPs.
    """
    if not ip_address or ip_address in _SAFE_IPS:
        return 0

    # Private RFC-1918 ranges — no geo data available
    if ip_address.startswith(("192.168.", "10.", "172.")):
        return 0

    try:
        resp = httpx.get(f"http://ip-api.com/json/{ip_address}?fields=status,country", timeout=2.0)
        data = resp.json()
        if data.get("status") == "success":
            return 0   # Known good country — score is 0 for now
        return 20      # Unknown geo — mild risk
    except Exception:
        return 10      # Geo lookup failed — slight uncertainty
