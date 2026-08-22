from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.checkin_models import DailyCheckin
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/insights", tags=["insights"])


class Insight(BaseModel):
    category: str
    title: str
    message: str
    priority: int


class InsightResponse(BaseModel):
    insights: list[Insight]
    engine: str = "rules-v1"
    external_ai_used: bool = False
    disclaimer: str = "Insights de autocuidado e acompanhamento; não constituem diagnóstico, prescrição ou orientação de emergência."


def build_insights(rows: list[DailyCheckin]) -> list[Insight]:
    if not rows:
        return [Insight(category="engagement", title="Comece seu acompanhamento", message="Faça seu primeiro check-in para começar a identificar padrões ao longo do tempo.", priority=1)]

    avg_mood = sum(r.mood for r in rows) / len(rows)
    avg_anxiety = sum(r.anxiety for r in rows) / len(rows)
    avg_energy = sum(r.energy for r in rows) / len(rows)
    avg_stress = sum(r.stress for r in rows) / len(rows)
    avg_sleep = sum(r.sleep_quality for r in rows) / len(rows)

    insights: list[Insight] = []
    if avg_sleep <= 4:
        insights.append(Insight(category="sleep", title="Sono merece atenção", message="Sua qualidade de sono recente ficou baixa. Observe rotina, horários e fatores que possam estar interferindo no descanso.", priority=1))
    if avg_stress >= 7:
        insights.append(Insight(category="stress", title="Estresse elevado recentemente", message="Os check-ins recentes mostram estresse percebido alto. Vale observar quais situações, horários ou compromissos coincidem com esses dias.", priority=1))
    if avg_anxiety >= 7:
        insights.append(Insight(category="anxiety", title="Ansiedade percebida acima do habitual", message="Sua média recente de ansiedade percebida está alta. Use o histórico para identificar gatilhos e considere buscar apoio profissional se isso persistir ou estiver prejudicando sua rotina.", priority=1))
    if avg_energy <= 4:
        insights.append(Insight(category="energy", title="Energia recente mais baixa", message="Sua energia ficou baixa nos últimos registros. Compare esse padrão com sono, estresse e carga de atividades.", priority=2))
    if avg_mood <= 4:
        insights.append(Insight(category="mood", title="Humor recente mais baixo", message="Seus registros mostram humor mais baixo recentemente. Acompanhe a evolução nos próximos dias e procure apoio profissional se houver persistência ou piora importante.", priority=1))

    if not insights:
        insights.append(Insight(category="trend", title="Padrão recente estável", message="Seus check-ins recentes não mostram nenhum sinal simples de atenção pelas regras atuais. Continue registrando para aumentar a qualidade do histórico.", priority=3))

    return sorted(insights, key=lambda item: item.priority)


@router.get("/me", response_model=InsightResponse)
def my_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InsightResponse:
    since = date.today() - timedelta(days=6)
    rows = db.scalars(
        select(DailyCheckin)
        .where(DailyCheckin.user_id == current_user.id, DailyCheckin.checkin_date >= since)
        .order_by(DailyCheckin.checkin_date.desc())
    ).all()
    return InsightResponse(insights=build_insights(list(rows)))
