from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.assessments import router as assessments_router
from app.auth import router as auth_router
from app.checkins import router as checkins_router
from app.core.config import settings
from app.dashboard import router as dashboard_router
from app.health_score import router as health_score_router
from app.insights import router as insights_router
from app.journal import router as journal_router
from app.profile import router as profile_router
from app.trails import router as trails_router

app = FastAPI(
    title=settings.app_name,
    version="0.11.0",
    description="API inicial do MVP de monitoramento de saúde mental.",
    docs_url="/docs" if settings.environment.lower() != "production" else None,
    redoc_url="/redoc" if settings.environment.lower() != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(assessments_router)
app.include_router(trails_router)
app.include_router(health_score_router)
app.include_router(checkins_router)
app.include_router(journal_router)
app.include_router(dashboard_router)
app.include_router(insights_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "vitapoint-api", "environment": settings.environment}


@app.get("/ready")
def readiness_check() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/")
def root() -> dict[str, str | None]:
    return {
        "name": settings.app_name,
        "status": "running",
        "environment": settings.environment,
        "docs": app.docs_url,
    }
