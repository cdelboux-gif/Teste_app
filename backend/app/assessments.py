import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment_models import AssessmentResponse, AssessmentSession
from app.auth import get_current_user
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/assessments", tags=["assessments"])


INSTRUMENT_CATALOG = {
    "WHO5": {
        "name": "WHO-5 Well-Being Index",
        "domain": "wellbeing",
        "content_available": False,
        "license_note": "Instrument content must be added only after licensing/usage validation.",
    },
    "BAI": {
        "name": "Beck Anxiety Inventory",
        "domain": "anxiety",
        "content_available": False,
        "license_note": "Proprietary instrument; questions are intentionally not embedded.",
    },
    "BDI": {
        "name": "Beck Depression Inventory",
        "domain": "depression",
        "content_available": False,
        "license_note": "Proprietary instrument; questions are intentionally not embedded.",
    },
    "ROSENBERG": {
        "name": "Rosenberg Self-Esteem Scale",
        "domain": "self_esteem",
        "content_available": False,
        "license_note": "Content publication/translation rights must be validated before embedding.",
    },
    "EAT26": {
        "name": "Eating Attitudes Test-26",
        "domain": "eating_behavior",
        "content_available": False,
        "license_note": "Content publication/usage rights must be validated before embedding.",
    },
    "DEMO_WELLBEING": {
        "name": "VitaPoint Demo Wellbeing Check",
        "domain": "wellbeing",
        "content_available": True,
        "license_note": "Internal non-diagnostic demo instrument for validating the MVP engine.",
        "items": [
            {"code": "energy", "prompt": "Como esteve sua energia hoje?", "min": 0, "max": 4},
            {"code": "calm", "prompt": "Quão calmo(a) você se sentiu hoje?", "min": 0, "max": 4},
            {"code": "interest", "prompt": "Quanto interesse você teve pelas suas atividades hoje?", "min": 0, "max": 4},
        ],
    },
}


class StartAssessmentRequest(BaseModel):
    instrument_code: str


class StartAssessmentResponse(BaseModel):
    session_id: uuid.UUID
    instrument_code: str
    instrument_version: str
    items: list[dict]


class AnswerItem(BaseModel):
    item_code: str
    numeric_value: int | None = Field(default=None, ge=0, le=10)
    text_value: str | None = Field(default=None, max_length=2000)


class SubmitAssessmentRequest(BaseModel):
    answers: list[AnswerItem] = Field(min_length=1, max_length=100)


class AssessmentResult(BaseModel):
    session_id: uuid.UUID
    instrument_code: str
    raw_score: int
    normalized_score: int
    classification: str
    disclaimer: str


def _score_demo(answers: list[AnswerItem]) -> tuple[int, int, str]:
    values = [a.numeric_value for a in answers if a.numeric_value is not None]
    if not values:
        raise ValueError("Nenhuma resposta numérica válida.")
    raw = sum(values)
    maximum = 4 * 3
    normalized = round((raw / maximum) * 100)
    if normalized >= 75:
        classification = "bem-estar percebido alto"
    elif normalized >= 50:
        classification = "bem-estar percebido intermediário"
    else:
        classification = "bem-estar percebido baixo"
    return raw, normalized, classification


@router.get("")
def list_assessments() -> list[dict]:
    return [
        {"code": code, **{k: v for k, v in data.items() if k != "items"}}
        for code, data in INSTRUMENT_CATALOG.items()
    ]


@router.get("/{instrument_code}")
def get_assessment(instrument_code: str) -> dict:
    instrument = INSTRUMENT_CATALOG.get(instrument_code.upper())
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrumento não encontrado.")
    return {"code": instrument_code.upper(), **instrument}


@router.post("/start", response_model=StartAssessmentResponse, status_code=status.HTTP_201_CREATED)
def start_assessment(
    payload: StartAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StartAssessmentResponse:
    code = payload.instrument_code.upper()
    instrument = INSTRUMENT_CATALOG.get(code)
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrumento não encontrado.")
    if not instrument.get("content_available"):
        raise HTTPException(status_code=409, detail="Conteúdo ainda não habilitado para uso no MVP.")

    session = AssessmentSession(
        user_id=current_user.id,
        instrument_code=code,
        instrument_version="1.0",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return StartAssessmentResponse(
        session_id=session.id,
        instrument_code=code,
        instrument_version=session.instrument_version,
        items=instrument.get("items", []),
    )


@router.post("/{session_id}/submit", response_model=AssessmentResult)
def submit_assessment(
    session_id: uuid.UUID,
    payload: SubmitAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentResult:
    session = db.scalar(
        select(AssessmentSession).where(
            AssessmentSession.id == session_id,
            AssessmentSession.user_id == current_user.id,
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    if session.status == "completed":
        raise HTTPException(status_code=409, detail="Avaliação já finalizada.")
    if session.instrument_code != "DEMO_WELLBEING":
        raise HTTPException(status_code=409, detail="Pontuação ainda não habilitada para este instrumento.")

    expected_codes = {"energy", "calm", "interest"}
    received_codes = {a.item_code for a in payload.answers}
    if received_codes != expected_codes:
        raise HTTPException(status_code=422, detail="Respostas incompletas ou inválidas.")
    for answer in payload.answers:
        if answer.numeric_value is None or not 0 <= answer.numeric_value <= 4:
            raise HTTPException(status_code=422, detail="Cada resposta deve estar entre 0 e 4.")
        db.add(
            AssessmentResponse(
                session_id=session.id,
                item_code=answer.item_code,
                numeric_value=answer.numeric_value,
                text_value=answer.text_value,
            )
        )

    try:
        raw, normalized, classification = _score_demo(payload.answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    disclaimer = "Resultado de autocuidado e monitoramento. Não constitui diagnóstico médico ou psicológico."
    session.raw_score = raw
    session.normalized_score = normalized
    session.classification = classification
    session.result_payload = {"disclaimer": disclaimer}
    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)
    db.commit()

    return AssessmentResult(
        session_id=session.id,
        instrument_code=session.instrument_code,
        raw_score=raw,
        normalized_score=normalized,
        classification=classification,
        disclaimer=disclaimer,
    )


@router.get("/history/me")
def assessment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    sessions = db.scalars(
        select(AssessmentSession)
        .where(AssessmentSession.user_id == current_user.id)
        .order_by(AssessmentSession.started_at.desc())
    ).all()
    return [
        {
            "session_id": s.id,
            "instrument_code": s.instrument_code,
            "status": s.status,
            "normalized_score": s.normalized_score,
            "classification": s.classification,
            "started_at": s.started_at,
            "completed_at": s.completed_at,
        }
        for s in sessions
    ]
