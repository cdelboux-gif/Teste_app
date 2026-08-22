from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VitaPoint Mental Health MVP API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://vitapoint:vitapoint@localhost:5432/vitapoint"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 30
    cors_origins: str = "http://localhost:8081,http://localhost:19006"
    forwarded_allow_ips: str = "*"
    log_level: str = "info"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.environment.lower() == "production":
            if self.jwt_secret_key == "change-me-in-production" or len(self.jwt_secret_key) < 32:
                raise ValueError("JWT_SECRET_KEY must be changed and contain at least 32 characters in production.")
            if "localhost" in self.database_url:
                raise ValueError("DATABASE_URL must point to a production database when ENVIRONMENT=production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
