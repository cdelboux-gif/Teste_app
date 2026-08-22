from app.dashboard import _next_actions


def test_dashboard_prompts_checkin_and_baseline_when_missing():
    actions = _next_actions({"completed_today": False}, {"score": None})
    types = [item["type"] for item in actions]
    assert "checkin" in types
    assert "assessment" in types
    assert "journal" in types


def test_dashboard_skips_completed_checkin_and_existing_score():
    actions = _next_actions({"completed_today": True}, {"score": 78})
    types = [item["type"] for item in actions]
    assert "checkin" not in types
    assert "assessment" not in types
    assert types == ["journal"]
