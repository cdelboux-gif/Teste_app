from fastapi import FastAPI

from app.auth import router as auth_router

app = FastAPI(
    title="VitaPoint Mental Health MVP API",
    version="0.2.0",
    description="API inicial do MVP de monitoramento de saúde mental.",
)

app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "vitapoint-api"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "VitaPoint Mental Health MVP API",
        "status": "running",
        "docs": "/docs",
    }
