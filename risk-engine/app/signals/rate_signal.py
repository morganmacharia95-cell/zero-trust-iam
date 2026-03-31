from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque

# Sliding window config
WINDOW_SECONDS = 60   # 1-minute window
MAX_REQUESTS   = 20   # requests allowed per user per window before flagging

# In-memory request timestamps per user_id
_request_log: dict[str, deque] = defaultdict(deque)


def rate_score(user_id: str) -> int:
    """
    Returns a risk score (0-100) based on request rate.
    Detects credential stuffing and brute-force patterns.
    Uses a sliding window counter per user_id.
    """
    now    = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=WINDOW_SECONDS)

    log = _request_log[user_id]

    # Evict timestamps outside the window
    while log and log[0] < cutoff:
        log.popleft()

    # Record this request
    log.append(now)
    count = len(log)

    if count <= MAX_REQUESTS:
        return 0

    # Exponential-ish scaling above threshold
    excess = count - MAX_REQUESTS
    score  = min(100, 40 + (excess * 6))
    return score
