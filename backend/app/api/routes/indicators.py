from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Indicator, Observation
from app.schemas import IndicatorRead, ObservationRead

router = APIRouter(prefix="/api/v1", tags=["indicators"])


@router.get("/indicators", response_model=list[IndicatorRead])
def list_indicators(db: Session = Depends(get_db)) -> list[Indicator]:
    return list(db.scalars(select(Indicator).order_by(Indicator.category, Indicator.name)).all())


@router.get("/indicators/{code}/observations", response_model=list[ObservationRead])
def list_observations(
    code: str,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=365, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[Observation]:
    indicator = db.scalar(select(Indicator).where(Indicator.code == code.upper()))
    if indicator is None:
        raise HTTPException(status_code=404, detail="Indicator not found")

    statement = select(Observation).where(Observation.indicator_id == indicator.id)
    if start_date is not None:
        statement = statement.where(Observation.observation_date >= start_date)
    if end_date is not None:
        statement = statement.where(Observation.observation_date <= end_date)
    statement = statement.order_by(Observation.observation_date.desc()).limit(limit)
    observations = list(db.scalars(statement).all())
    return list(reversed(observations))
