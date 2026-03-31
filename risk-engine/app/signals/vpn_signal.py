import httpx

# Known Tor exit node list URL (public)
_TOR_EXIT_NODES: set[str] = set()
_TOR_LOADED = False

# IPs that are never flagged
_SAFE_IPS = {"127.0.0.1", "::1"}


def _load_tor_exits():
    """Loads Tor exit node IPs from the public Dan.me.uk list."""
    global _TOR_EXIT_NODES, _TOR_LOADED
    if _TOR_LOADED:
        return
    try:
        resp = httpx.get(
            "https://check.torproject.org/torbulkexitlist",
            timeout=5.0,
        )
        _TOR_EXIT_NODES = set(resp.text.strip().splitlines())
        _TOR_LOADED = True
    except Exception:
        # If the list can't load, fail open (don't block everyone)
        _TOR_LOADED = True


def vpn_score(ip_address: str) -> int:
    """
    Returns a risk score (0-100) based on whether the IP is a
    known Tor exit node. VPN detection would require a paid API
    (e.g. ip-api.com Pro) — Tor detection is free and sufficient for demo.
    """
    if not ip_address or ip_address in _SAFE_IPS:
        return 0

    if ip_address.startswith(("192.168.", "10.", "172.")):
        return 0   # Private IP — not a VPN

    _load_tor_exits()

    if ip_address in _TOR_EXIT_NODES:
        return 100  # Confirmed Tor exit — maximum risk

    return 0
