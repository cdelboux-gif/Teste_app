import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.journal_models import JournalEntry
from app.models import User

router = APIRouter(prefix="/journal", tags=["journal"])


class JournalCreate(BaseModel):
    title: str | None = Field(default=None, max_length=160)
    content: str = Field(min_length=1, max_length=10000)
    mood_label: str | None = Field(default=None, max_length=40)


class JournalUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=160)
    content: str = Field(min_length=1, max_length=10000)
    mood_label: str | None = Field(default=None, max_length=40)


class JournalResponse(JournalCreate):
    id: uuid.UUID


def _owned_entry(entry_id: uuid.UUID, user: User, db: Session) -> JournalEntry:
    row = db.scalar(select(JournalEntry).where(JournalEntry.id == entry_id, JournalEntry.user_id == user.id))
    if row is None:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")
    return row


@router.post("", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
def create_entry(payload: JournalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = JournalEntry(user_id=current_user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return JournalResponse(id=row.id, title=row.title, content=row.content, mood_label=row.mood_label)


@router.get("", response_model=list[JournalResponse])
def list_entries(limit: int = Query(default=30, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(JournalEntry).where(JournalEntry.user_id == current_user.id).order_by(JournalEntry.created_at.desc()).limit(limit)).all()
    return [JournalResponse(id=r.id, title=r.title, content=r.content, mood_label=r.mood_label) for r in rows]


@router.get("/{entry_id}", response_model=JournalResponse)
def get_entry(entry_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = _owned_entry(entry_id, current_user, db)
    return JournalResponse(id=row.id, title=row.title, content=row.content, mood_label=row.mood_label)


@router.put("/{entry_id}", response_model=JournalResponse)
def update_entry(entry_id: uuid.UUID, payload: JournalUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = _owned_entry(entry_id, current_user, db)
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return JournalResponse(id=row.id, title=row.title, content=row.content, mood_label=row.mood_label)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = _owned_entry(entry_id, current_user, db)
    db.delete(row)
    db.commit()
