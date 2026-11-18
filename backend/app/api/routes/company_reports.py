from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CompanyReport
from app.schemas.company_reports import CompanyReportAnalysis, CompanyReportRead

router = APIRouter(prefix="/api/v1/company-reports", tags=["company reports"])


def calculate_ratios(financials: dict[str, float]) -> dict[str, float | None]:
    """Calculate common ratios only from explicitly reviewed financial values."""
    def divide(numerator: str, denominator: str) -> float | None:
        top, bottom = financials.get(numerator), financials.get(denominator)
        if top is None or bottom in (None, 0):
            return None
        return top / bottom

    return {
        "current_ratio": divide("current_assets", "current_liabilities"),
        "debt_to_equity": divide("total_debt", "total_equity"),
        "gross_margin": divide("gross_profit", "revenue"),
        "net_margin": divide("net_income", "revenue"),
        "return_on_assets": divide("net_income", "total_assets"),
        "return_on_equity": divide("net_income", "total_equity"),
        "operating_cash_flow_to_current_liabilities": divide(
            "operating_cash_flow", "current_liabilities"
        ),
    }


@router.get("", response_model=list[CompanyReportRead])
def list_company_reports(
    symbol: str | None = Query(default=None, min_length=1, max_length=32),
    report_type: str | None = Query(default=None, pattern="^(annual|half_yearly)$"),
    fiscal_year: int | None = Query(default=None, ge=1900, le=2200),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[CompanyReport]:
    statement = select(CompanyReport)
    if symbol:
        statement = statement.where(CompanyReport.symbol == symbol.upper())
    if report_type:
        statement = statement.where(CompanyReport.report_type == report_type)
    if fiscal_year:
        statement = statement.where(CompanyReport.fiscal_year == fiscal_year)
    statement = statement.order_by(CompanyReport.fiscal_year.desc(), CompanyReport.id.desc()).limit(limit)
    return list(db.scalars(statement).all())


@router.get("/{report_id}/analysis", response_model=CompanyReportAnalysis)
def get_report_analysis(report_id: int, db: Session = Depends(get_db)) -> CompanyReportAnalysis:
    report = db.get(CompanyReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Company report not found")
    financials = report.reviewed_financials or {}
    return CompanyReportAnalysis(
        report_id=report.id,
        symbol=report.symbol,
        company_name=report.company_name,
        fiscal_year=report.fiscal_year,
        report_type=report.report_type,
        review_status=report.review_status,
        financials=financials,
        ratios=calculate_ratios(financials),
        note=(
            "Figures and ratios are based only on reviewed structured financial data. "
            "Extracted PDF text and statement excerpts are not verified figures."
        ),
    )
