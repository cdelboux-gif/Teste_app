from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.checkin_models import DailyCheckin
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/checkins", tags=["check-ins"])


class CheckinPayload(BaseModel):
    mood: int = Field(ge=0, le=10)
    anxiety: int = Field(ge=0, le=10)
    energy: int = Field(ge=0, le=10)
    stress: int = Field(ge=0, le=10)
    sleep_quality: int = Field(ge=0, le=10)
    note: str | None = Field(default=None, max_length=1000)


class CheckinResponse(CheckinPayload):
    id: str
    checkin_date: date
    source: str


def _serialize(row: DailyCheckin) -> CheckinResponse:
    return CheckinResponse(
        id=str(row.id),
        checkin_date=row.checkin_date,
        mood=row.mood,
        anxiety=row.anxiety,
        energy=row.energy,
        stress=row.stress,
        sleep_quality=row.sleep_quality,
        note=row.note,
        source=row.source,
    )


@router.post("/today", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
def create_today_checkin(
    payload: CheckinPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckinResponse:
    today = date.today()
    existing = db.scalar(
        select(DailyCheckin).where(
            DailyCheckin.user_id == current_user.id,
            DailyCheckin.checkin_date == today,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Check-in de hoje já realizado.")

    row = DailyCheckin(user_id=current_user.id, checkin_date=today, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize(row)


@router.put("/today", response_model=CheckinResponse)
def update_today_checkin(
    payload: CheckinPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckinResponse:
    row = db.scalar(
        select(DailyCheckin).where(
            DailyCheckin.user_id == current_user.id,
            DailyCheckin.checkin_date == date.today(),
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Check-in de hoje ainda não existe.")
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return _serialize(row)


@router.get("/today", response_model=CheckinResponse | None)
def get_today_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.scalar(
        select(DailyCheckin).where(
            DailyCheckin.user_id == current_user.id,
            DailyCheckin.checkin_date == date.today(),
        )
    )
    return _serialize(row) if row else None


@router.get("/history", response_model=list[CheckinResponse])
def checkin_history(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CheckinResponse]:
    since = date.today() - timedelta(days=days - 1)
    rows = db.scalars(
        select(DailyCheckin)
        .where(DailyCheckin.user_id == current_user.id, DailyCheckin.checkin_date >= since)
        .order_by(DailyCheckin.checkin_date.desc())
    ).all()
    return [_serialize(row) for row in rows]
