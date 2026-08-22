from types import SimpleNamespace

from app.insights import build_insights


def row(mood=7, anxiety=3, energy=7, stress=3, sleep_quality=8):
    return SimpleNamespace(mood=mood, anxiety=anxiety, energy=energy, stress=stress, sleep_quality=sleep_quality)


def test_empty_history_prompts_first_checkin():
    insights = build_insights([])
    assert insights[0].category == "engagement"


def test_low_sleep_generates_sleep_insight():
    insights = build_insights([row(sleep_quality=3)])
    assert any(item.category == "sleep" for item in insights)


def test_high_anxiety_generates_anxiety_insight():
    insights = build_insights([row(anxiety=8)])
    assert any(item.category == "anxiety" for item in insights)


def test_stable_pattern_generates_trend_insight():
    insights = build_insights([row()])
    assert insights[0].category == "trend"
