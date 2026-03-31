import hashlib

# In-memory store: user_id -> set of known device fingerprints
_known_devices: dict[str, set[str]] = {}


def _fingerprint(user_agent: str) -> str:
    """Creates a short hash of the User-Agent string as a device fingerprint."""
    return hashlib.sha256(user_agent.encode()).hexdigest()[:16]


def device_score(user_agent: str, user_id: str) -> int:
    """
    Returns a risk score (0-100) for device recognition.
    New/unrecognised devices get a higher score on first seen.
    Score drops to 0 once device is registered for that user.
    """
    if not user_agent or not user_id:
        return 20

    fp = _fingerprint(user_agent)

    if user_id not in _known_devices:
        # First time we've seen this user — register the device
        _known_devices[user_id] = {fp}
        return 0   # First login — not suspicious

    if fp not in _known_devices[user_id]:
        # Known user, new device
        _known_devices[user_id].add(fp)
        return 70  # New device = higher risk

    return 0  # Known device = no risk
