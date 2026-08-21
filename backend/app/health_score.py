from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment_models import AssessmentSession
from app.auth import get_current_user
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/health-score", tags=["health-score"])

# Product-level wellbeing index. It is intentionally not a clinical score.
# Domain directions let us later combine validated instruments without
# treating the composite number as diagnosis or medical risk prediction.
DOMAIN_DIRECTION = {
    "wellbeing": "positive",
    "self_esteem": "positive",
    "anxiety": "negative",
    "depression": "negative",
    "stress": "negative",
    "burnout": "negative",
    "sleep_difficulty": "negative",
    "eating_behavior": "negative",
}

INSTRUMENT_DOMAIN = {
    "DEMO_WELLBEING": "wellbeing",
    "WHO5": "wellbeing",
    "BAI": "anxiety",
    "BDI": "depression",
    "ROSENBERG": "self_esteem",
    "EAT26": "eating_behavior",
}


class ScoreComponent(BaseModel):
    instrument_code: str
    domain: str
    source_score: int = Field(ge=0, le=100)
    contribution_score: int = Field(ge=0, le=100)


class HealthScoreResponse(BaseModel):
    score: int | None
    status: str
    components: list[ScoreComponent]
    generated_at: datetime
    disclaimer: str


def contribution_score(normalized_score: int, direction: str) -> int:
    bounded = max(0, min(100, normalized_score))
    return bounded if direction == "positive" else 100 - bounded


def aggregate_components(components: list[int]) -> int | None:
    if not components:
        return None
    return round(sum(components) / len(components))


def score_status(score: int | None) -> str:
    if score is None:
        return "baseline_pending"
    if score >= 75:
        return "stable"
    if score >= 50:
        return "attention"
    return "needs_attention"


@router.get("/me", response_model=HealthScoreResponse)
def my_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthScoreResponse:
    completed = db.scalars(
        select(AssessmentSession)
        .where(
            AssessmentSession.user_id == current_user.id,
            AssessmentSession.status == "completed",
            AssessmentSession.normalized_score.is_not(None),
        )
        .order_by(AssessmentSession.completed_at.desc())
    ).all()

    # Use only the latest completed result for each instrument to avoid
    # overweighting instruments repeated more frequently than others.
    latest_by_instrument = {}
    for session in completed:
        latest_by_instrument.setdefault(session.instrument_code, session)

    components = []
    values = []
    for code, session in latest_by_instrument.items():
        domain = INSTRUMENT_DOMAIN.get(code)
        if domain is None:
            continue
        direction = DOMAIN_DIRECTION[domain]
        contribution = contribution_score(session.normalized_score, direction)
        components.append(
            ScoreComponent(
                instrument_code=code,
                domain=domain,
                source_score=session.normalized_score,
                contribution_score=contribution,
            )
        )
        values.append(contribution)

    score = aggregate_components(values)
    return HealthScoreResponse(
        score=score,
        status=score_status(score),
        components=components,
        generated_at=datetime.utcnow(),
        disclaimer=(
            "VitaPoint Health Score é um índice de acompanhamento do produto, não validado como "
            "instrumento diagnóstico e não substitui avaliação de profissional de saúde."
        ),
    )
