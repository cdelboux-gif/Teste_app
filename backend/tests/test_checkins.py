import pytest
from pydantic import ValidationError

from app.checkins import CheckinPayload


def test_valid_checkin_payload():
    payload = CheckinPayload(mood=8, anxiety=3, energy=7, stress=4, sleep_quality=8)
    assert payload.mood == 8
    assert payload.sleep_quality == 8


def test_checkin_metrics_are_bounded():
    with pytest.raises(ValidationError):
        CheckinPayload(mood=11, anxiety=3, energy=7, stress=4, sleep_quality=8)


def test_note_length_is_limited():
    with pytest.raises(ValidationError):
        CheckinPayload(mood=5, anxiety=5, energy=5, stress=5, sleep_quality=5, note="x" * 1001)
