import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../risk-engine"))

from app.scorer import calculate_risk, score_to_level
from app.signals.time_signal import time_score
from app.signals.rate_signal import rate_score
from app.signals.device_signal import device_score


def test_risk_score_is_bounded():
    result = calculate_risk("user1", "alice", "127.0.0.1", "Mozilla/5.0")
    assert 0 <= result["score"] <= 100


def test_risk_level_present():
    result = calculate_risk("user2", "bob", "127.0.0.1", "Mozilla/5.0")
    assert result["level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def test_score_to_level_low():
    assert score_to_level(15) == "LOW"

def test_score_to_level_medium():
    assert score_to_level(45) == "MEDIUM"

def test_score_to_level_high():
    assert score_to_level(70) == "HIGH"

def test_score_to_level_critical():
    assert score_to_level(90) == "CRITICAL"


def test_rate_signal_clean_user():
    score = rate_score("brand-new-user-xyz")
    assert score == 0


def test_rate_signal_spikes_on_many_requests():
    uid = "spammer-user-test"
    for _ in range(25):
        rate_score(uid)
    score = rate_score(uid)
    assert score > 0


def test_new_device_flagged():
    score = device_score("NewBrowser/9.0 UnknownAgent", "unique-user-device-test")
    # Second call with different UA should trigger
    score2 = device_score("TotallyDifferentBrowser/1.0", "unique-user-device-test")
    assert score2 > 0


def test_known_device_not_flagged():
    ua  = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    uid = "known-device-user"
    device_score(ua, uid)   # register
    score = device_score(ua, uid)  # second time — should be 0
    assert score == 0
