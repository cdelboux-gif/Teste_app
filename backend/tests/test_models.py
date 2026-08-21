from app.models import Profile, User


def test_user_model_metadata() -> None:
    assert User.__tablename__ == "users"
    assert "email" in User.__table__.columns
    assert "password_hash" in User.__table__.columns


def test_profile_model_metadata() -> None:
    assert Profile.__tablename__ == "profiles"
    assert "user_id" in Profile.__table__.columns
    assert "onboarding_completed" in Profile.__table__.columns
