from app.trails import TRAILS, _goal_to_trail


def test_baseline_trail_exists():
    assert "baseline" in TRAILS
    assert "DEMO_WELLBEING" in TRAILS["baseline"]["instruments"]


def test_goal_routes_to_anxiety_trail():
    assert _goal_to_trail("Quero reduzir minha ansiedade") == "anxiety_stress"


def test_goal_routes_to_self_esteem_trail():
    assert _goal_to_trail("Quero melhorar minha autoestima") == "self_esteem"


def test_unknown_goal_falls_back_to_baseline():
    assert _goal_to_trail("Quero acompanhar minha saúde") == "baseline"
