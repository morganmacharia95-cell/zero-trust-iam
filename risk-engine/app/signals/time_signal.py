from datetime import datetime, timezone

# Normal working hours (UTC). Adjust per your user base timezone.
WORK_HOURS_START = 6   # 6am UTC
WORK_HOURS_END   = 20  # 8pm UTC

# Weekend days (0=Monday, 6=Sunday)
WEEKEND_DAYS = {5, 6}


def time_score(user_id: str) -> int:
    """
    Returns a risk score (0-100) based on time of access.
    After-hours and weekend logins are flagged as higher risk.
    """
    now     = datetime.now(timezone.utc)
    hour    = now.hour
    weekday = now.weekday()

    score = 0

    # Weekend access — moderate flag
    if weekday in WEEKEND_DAYS:
        score += 30

    # Middle-of-night access (10pm–5am UTC)
    if hour < WORK_HOURS_START or hour >= WORK_HOURS_END:
        score += 50

    return min(100, score)
