from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment_models import AssessmentSession
from app.auth import get_current_user
from app.checkin_models import DailyCheckin
from app.db import get_db
from app.health_score import DOMAIN_DIRECTION, INSTRUMENT_DOMAIN, aggregate_components, contribution_score, score_status
from app.models import User
from app.trails import TRAILS, _goal_to_trail

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _health_score_snapshot(user_id, db: Session) -> dict:
    completed = db.scalars(
        select(AssessmentSession)
        .where(
            AssessmentSession.user_id == user_id,
            AssessmentSession.status == "completed",
            AssessmentSession.normalized_score.is_not(None),
        )
        .order_by(AssessmentSession.completed_at.desc())
    ).all()

    latest = {}
    for session in completed:
        latest.setdefault(session.instrument_code, session)

    values = []
    for code, session in latest.items():
        domain = INSTRUMENT_DOMAIN.get(code)
        if domain is None:
            continue
        values.append(contribution_score(session.normalized_score, DOMAIN_DIRECTION[domain]))

    score = aggregate_components(values)
    return {"score": score, "status": score_status(score), "component_count": len(values)}


def _checkin_snapshot(user_id, db: Session) -> dict:
    today = db.scalar(
        select(DailyCheckin).where(
            DailyCheckin.user_id == user_id,
            DailyCheckin.checkin_date == date.today(),
        )
    )
    if today is None:
        return {"completed_today": False, "today": None}
    return {
        "completed_today": True,
        "today": {
            "mood": today.mood,
            "anxiety": today.anxiety,
            "energy": today.energy,
            "stress": today.stress,
            "sleep_quality": today.sleep_quality,
        },
    }


def _trend_snapshot(user_id, db: Session, days: int = 7) -> dict:
    since = date.today() - timedelta(days=days - 1)
    rows = db.scalars(
        select(DailyCheckin)
        .where(DailyCheckin.user_id == user_id, DailyCheckin.checkin_date >= since)
        .order_by(DailyCheckin.checkin_date.asc())
    ).all()
    if not rows:
        return {"days_with_data": 0, "averages": None}

    def avg(field: str) -> float:
        return round(sum(getattr(row, field) for row in rows) / len(rows), 1)

    return {
        "days_with_data": len(rows),
        "averages": {
            "mood": avg("mood"),
            "anxiety": avg("anxiety"),
            "energy": avg("energy"),
            "stress": avg("stress"),
            "sleep_quality": avg("sleep_quality"),
        },
    }


def _next_actions(checkin: dict, health_score: dict) -> list[dict]:
    actions = []
    if not checkin["completed_today"]:
        actions.append({"type": "checkin", "title": "Faça seu check-in de hoje", "priority": 1})
    if health_score["score"] is None:
        actions.append({"type": "assessment", "title": "Complete sua avaliação inicial", "priority": 2})
    actions.append({"type": "journal", "title": "Registrar como foi seu dia", "priority": 3})
    return actions


@router.get("/home")
def dashboard_home(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    profile = current_user.profile
    trail_code = _goal_to_trail(profile.primary_goal if profile else None)
    trail = TRAILS[trail_code]
    health_score = _health_score_snapshot(current_user.id, db)
    checkin = _checkin_snapshot(current_user.id, db)

    return {
        "user": {
            "first_name": (profile.full_name.split()[0] if profile and profile.full_name else None),
            "onboarding_completed": bool(profile and profile.onboarding_completed),
        },
        "health_score": health_score,
        "checkin": checkin,
        "trend_7d": _trend_snapshot(current_user.id, db),
        "recommended_trail": {
            "code": trail_code,
            "name": trail["name"],
            "description": trail["description"],
        },
        "next_actions": _next_actions(checkin, health_score),
        "disclaimer": "Painel de acompanhamento e autocuidado. Não constitui diagnóstico ou prescrição clínica.",
    }
