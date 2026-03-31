from app.signals.geo_signal import geo_score
from app.signals.time_signal import time_score
from app.signals.device_signal import device_score
from app.signals.rate_signal import rate_score
from app.signals.vpn_signal import vpn_score

# Risk level thresholds
THRESHOLDS = {
    "LOW":      (0,  30),
    "MEDIUM":   (31, 60),
    "HIGH":     (61, 80),
    "CRITICAL": (81, 100),
}

# Signal weights — must sum to 100
WEIGHTS = {
    "geo":    25,
    "time":   15,
    "device": 20,
    "rate":   25,
    "vpn":    15,
}


def calculate_risk(
    user_id:    str,
    username:   str,
    ip_address: str,
    user_agent: str,
) -> dict:
    """
    Runs all 5 risk signals and returns an aggregated score + breakdown.

    Returns:
        {
          score: int (0-100),
          level: str (LOW | MEDIUM | HIGH | CRITICAL),
          signals: { geo: int, time: int, device: int, rate: int, vpn: int },
          factors: [str]   -- human-readable list of triggered risk factors
        }
    """
    signals = {
        "geo":    geo_score(ip_address),
        "time":   time_score(user_id),
        "device": device_score(user_agent, user_id),
        "rate":   rate_score(user_id),
        "vpn":    vpn_score(ip_address),
    }

    # Weighted sum
    raw_score = sum(
        signals[name] * (WEIGHTS[name] / 100)
        for name in signals
    )
    final_score = min(100, max(0, round(raw_score)))

    # Determine level
    level = "LOW"
    for lvl, (lo, hi) in THRESHOLDS.items():
        if lo <= final_score <= hi:
            level = lvl
            break

    # Collect human-readable factors for signals that fired
    factors = []
    if signals["geo"] > 50:
        factors.append(f"Unusual geolocation for IP {ip_address}")
    if signals["time"] > 50:
        factors.append("Login outside normal working hours")
    if signals["device"] > 50:
        factors.append("Unrecognised device fingerprint")
    if signals["rate"] > 50:
        factors.append("High request rate — possible credential stuffing")
    if signals["vpn"] > 50:
        factors.append("VPN or Tor exit node detected")

    return {
        "score":   final_score,
        "level":   level,
        "signals": signals,
        "factors": factors,
    }


def score_to_level(score: int) -> str:
    for lvl, (lo, hi) in THRESHOLDS.items():
        if lo <= score <= hi:
            return lvl
    return "CRITICAL"
