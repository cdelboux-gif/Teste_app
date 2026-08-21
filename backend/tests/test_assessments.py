from app.assessments import AnswerItem, INSTRUMENT_CATALOG, _score_demo


def test_catalog_keeps_proprietary_content_disabled() -> None:
    assert INSTRUMENT_CATALOG["BAI"]["content_available"] is False
    assert INSTRUMENT_CATALOG["BDI"]["content_available"] is False


def test_demo_scoring() -> None:
    answers = [
        AnswerItem(item_code="energy", numeric_value=4),
        AnswerItem(item_code="calm", numeric_value=3),
        AnswerItem(item_code="interest", numeric_value=2),
    ]
    raw, normalized, classification = _score_demo(answers)
    assert raw == 9
    assert normalized == 75
    assert classification == "bem-estar percebido alto"
