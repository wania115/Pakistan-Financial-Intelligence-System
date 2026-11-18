from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class IndicatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    category: str
    unit: str
    frequency: str
    description: str


class ObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_date: datetime
    value: float
    quality_status: str
    source_release_date: datetime | None = None


class HealthRead(BaseModel):
    status: str
    date: date
