from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database import Base


class CompanyReport(Base):
    __tablename__ = "company_reports"
    __table_args__ = (UniqueConstraint("source_url", name="uq_company_reports_source_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    company_name: Mapped[str] = mapped_column(String(200), index=True)
    report_type: Mapped[str] = mapped_column(String(24), index=True)
    fiscal_year: Mapped[int] = mapped_column(index=True)
    source_url: Mapped[str] = mapped_column(String(1000))
    source_name: Mapped[str] = mapped_column(String(100), default="Pakistan Stock Exchange")
    extracted_text: Mapped[str] = mapped_column(Text)
    statement_sections: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # Populated only by a reviewed financial-data workflow; raw PDF text is not treated as fact.
    reviewed_financials: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    review_status: Mapped[str] = mapped_column(String(24), default="needs_review", index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
