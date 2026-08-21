from datetime import date

from app.schemas import OnboardingRequest


def test_onboarding_payload_accepts_required_fields() -> None:
    payload = OnboardingRequest(
        full_name="Usuário Teste",
        birth_date=date(1990, 1, 1),
        gender="nao_informado",
        primary_goal="acompanhar bem-estar",
        consent_to_health_data=True,
        consent_to_ai_processing=True,
    )

    assert payload.full_name == "Usuário Teste"
    assert payload.timezone == "America/Sao_Paulo"
    assert payload.consent_version == "2026-08-v1"
