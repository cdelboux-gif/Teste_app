import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    is_active: bool


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str | None
    birth_date: date | None
    gender: str | None
    timezone: str
    primary_goal: str | None
    onboarding_completed: bool
    consent_version: str | None
    consented_at: datetime | None


class OnboardingRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    birth_date: date | None = None
    gender: str | None = Field(default=None, max_length=40)
    timezone: str = Field(default="America/Sao_Paulo", min_length=3, max_length=64)
    primary_goal: str = Field(min_length=2, max_length=120)
    consent_to_health_data: bool
    consent_to_ai_processing: bool
    consent_version: str = Field(default="2026-08-v1", min_length=1, max_length=40)


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    birth_date: date | None = None
    gender: str | None = Field(default=None, max_length=40)
    timezone: str | None = Field(default=None, min_length=3, max_length=64)
    primary_goal: str | None = Field(default=None, min_length=2, max_length=120)
