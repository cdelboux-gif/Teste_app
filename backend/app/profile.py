from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Profile, User
from app.schemas import OnboardingRequest, ProfileResponse, ProfileUpdateRequest

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    profile = current_user.profile
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil ainda não criado.")
    return profile


@router.post("/onboarding", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def complete_onboarding(
    payload: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    if not payload.consent_to_health_data or not payload.consent_to_ai_processing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Os consentimentos obrigatórios devem ser aceitos para concluir o onboarding.",
        )

    profile = current_user.profile
    if profile is None:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    profile.full_name = payload.full_name.strip()
    profile.birth_date = payload.birth_date
    profile.gender = payload.gender
    profile.timezone = payload.timezone
    profile.primary_goal = payload.primary_goal.strip()
    profile.onboarding_completed = True
    profile.consent_version = payload.consent_version
    profile.consented_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(profile)
    return profile


@router.patch("", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    profile = current_user.profile
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil ainda não criado.")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
