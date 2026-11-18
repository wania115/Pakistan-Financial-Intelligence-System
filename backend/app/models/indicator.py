from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    indicators: Mapped[list["Indicator"]] = relationship(back_populates="source")


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80), index=True)
    unit: Mapped[str] = mapped_column(String(40))
    frequency: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    source_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped[DataSource | None] = relationship(back_populates="indicators")
    observations: Mapped[list["Observation"]] = relationship(
        back_populates="indicator", cascade="all, delete-orphan"
    )


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    indicator_id: Mapped[int] = mapped_column(index=True)
    observation_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)
    value: Mapped[float]
    source_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    source_release_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    quality_status: Mapped[str] = mapped_column(String(40), default="unreviewed", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    indicator: Mapped[Indicator] = relationship(back_populates="observations")
