from app.health_score import aggregate_components, contribution_score, score_status


def test_positive_domain_preserves_score():
    assert contribution_score(80, "positive") == 80


def test_negative_domain_inverts_score():
    assert contribution_score(80, "negative") == 20


def test_aggregate_components():
    assert aggregate_components([80, 60, 70]) == 70


def test_empty_components_has_no_score():
    assert aggregate_components([]) is None
    assert score_status(None) == "baseline_pending"


def test_status_bands():
    assert score_status(80) == "stable"
    assert score_status(60) == "attention"
    assert score_status(40) == "needs_attention"
