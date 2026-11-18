from typing import Any

from pydantic import BaseModel, ConfigDict


class CompanyReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    company_name: str
    report_type: str
    fiscal_year: int
    source_url: str
    source_name: str
    statement_sections: dict[str, Any]
    review_status: str


class CompanyReportAnalysis(BaseModel):
    report_id: int
    symbol: str
    company_name: str
    fiscal_year: int
    report_type: str
    review_status: str
    financials: dict[str, Any]
    ratios: dict[str, float | None]
    note: str
