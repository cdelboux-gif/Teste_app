from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/trails", tags=["trails"])

TRAILS = {
    "baseline": {
        "name": "Mapa Inicial",
        "description": "Cria uma linha de base de bem-estar e direciona as próximas avaliações.",
        "instruments": ["DEMO_WELLBEING", "WHO5", "BAI", "BDI", "ROSENBERG"],
    },
    "anxiety_stress": {
        "name": "Ansiedade e Estresse",
        "description": "Acompanha sinais relacionados a ansiedade, estresse percebido, sono e bem-estar.",
        "instruments": ["BAI", "WHO5"],
    },
    "self_esteem": {
        "name": "Autoestima e Autopercepção",
        "description": "Acompanha autoestima, bem-estar e evolução da autopercepção.",
        "instruments": ["ROSENBERG", "WHO5"],
    },
    "eating_behavior": {
        "name": "Comportamento Alimentar",
        "description": "Organiza avaliações de comportamento alimentar e bem-estar associado.",
        "instruments": ["EAT26", "WHO5"],
    },
}


def _goal_to_trail(primary_goal: str | None) -> str:
    if not primary_goal:
        return "baseline"
    goal = primary_goal.lower()
    if any(term in goal for term in ("ansiedade", "estresse", "stress", "calma")):
        return "anxiety_stress"
    if any(term in goal for term in ("autoestima", "confiança", "autoconhecimento")):
        return "self_esteem"
    if any(term in goal for term in ("aliment", "comida", "compuls")):
        return "eating_behavior"
    return "baseline"


@router.get("")
def list_trails() -> list[dict]:
    return [{"code": code, **data} for code, data in TRAILS.items()]


@router.get("/recommended")
def recommended_trail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    # Regra MVP determinística e auditável. A camada de IA poderá ranquear
    # recomendações no futuro, mas nunca deve transformar triagem em diagnóstico.
    profile = current_user.profile
    trail_code = _goal_to_trail(profile.primary_goal if profile else None)
    trail = TRAILS[trail_code]
    return {
        "code": trail_code,
        **trail,
        "reason": "Recomendação baseada no objetivo informado no onboarding.",
        "clinical_disclaimer": "A trilha é de monitoramento e autocuidado; não constitui diagnóstico ou prescrição.",
    }


@router.get("/{trail_code}")
def get_trail(trail_code: str) -> dict:
    trail = TRAILS.get(trail_code)
    if trail is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    return {"code": trail_code, **trail}
