from __future__ import annotations

import argparse
import io
import re
import sys
from urllib.parse import urlparse

import httpx
from pypdf import PdfReader
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import CompanyReport

ALLOWED_HOSTS = {"financials.psx.com.pk", "dps.psx.com.pk", "psx.com.pk", "www.psx.com.pk"}
MAX_PDF_BYTES = 30 * 1024 * 1024
SECTION_HEADINGS = {
    "balance_sheet": ("statement of financial position", "balance sheet"),
    "income_statement": ("statement of profit or loss", "income statement", "profit and loss"),
    "cash_flow": ("statement of cash flows", "cash flow statement"),
}
ALL_HEADINGS = tuple(heading for headings in SECTION_HEADINGS.values() for heading in headings)


def validate_psx_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password:
        raise ValueError("Report URL must be HTTPS and hosted on an approved PSX domain")


def download_pdf(url: str) -> bytes:
    current_url = url
    headers = {"User-Agent": "PFIS research tool/0.1 (public company report processing)"}
    with httpx.Client(timeout=httpx.Timeout(30.0), follow_redirects=False, headers=headers) as client:
        for _ in range(4):
            validate_psx_url(current_url)
            with client.stream("GET", current_url) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        raise ValueError("PSX returned a redirect without a target")
                    from urllib.parse import urljoin

                    current_url = urljoin(current_url, location)
                    continue
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if "pdf" not in content_type and not current_url.lower().endswith(".pdf"):
                    raise ValueError("PSX report URL did not return a PDF")
                chunks: list[bytes] = []
                size = 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > MAX_PDF_BYTES:
                        raise ValueError("PDF exceeds the 30 MB processing limit")
                    chunks.append(chunk)
                content = b"".join(chunks)
                if not content.startswith(b"%PDF-"):
                    raise ValueError("Downloaded file is not a valid PDF")
                return content
    raise ValueError("Too many redirects while fetching report")


def extract_pdf_text(pdf_content: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_content), strict=False)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported")
    if len(reader.pages) > 1000:
        raise ValueError("PDF exceeds the 1,000-page processing limit")
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise ValueError("No selectable text found; OCR is not enabled for this report")
    return text[:5_000_000]


def extract_statement_sections(text: str) -> dict[str, str]:
    normalized = text.replace("\r", "\n")
    found: list[tuple[int, str]] = []
    for key, headings in SECTION_HEADINGS.items():
        positions = [normalized.lower().find(heading) for heading in headings]
        positions = [position for position in positions if position >= 0]
        if positions:
            found.append((min(positions), key))
    found.sort()
    sections: dict[str, str] = {}
    for index, (start, key) in enumerate(found):
        end = found[index + 1][0] if index + 1 < len(found) else min(len(normalized), start + 12000)
        sections[key] = re.sub(r"\n{3,}", "\n\n", normalized[start:end]).strip()[:12000]
    return sections


def ingest_report(symbol: str, company_name: str, report_type: str, fiscal_year: int, source_url: str) -> int:
    validate_psx_url(source_url)
    pdf = download_pdf(source_url)
    text = extract_pdf_text(pdf)
    sections = extract_statement_sections(text)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        report = db.scalar(select(CompanyReport).where(CompanyReport.source_url == source_url))
        if report is None:
            report = CompanyReport(
                symbol=symbol.upper(),
                company_name=company_name,
                report_type=report_type,
                fiscal_year=fiscal_year,
                source_url=source_url,
                extracted_text=text,
                statement_sections=sections,
                reviewed_financials={},
                review_status="needs_review",
            )
            db.add(report)
        else:
            report.symbol = symbol.upper()
            report.company_name = company_name
            report.report_type = report_type
            report.fiscal_year = fiscal_year
            report.extracted_text = text
            report.statement_sections = sections
            report.review_status = "needs_review"
        db.commit()
        db.refresh(report)
        return report.id


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and extract a PSX company report PDF")
    parser.add_argument("--symbol", required=True, help="PSX ticker symbol")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--period", required=True, choices=("annual", "half_yearly"))
    parser.add_argument("--fiscal-year", required=True, type=int)
    parser.add_argument("--url", required=True, help="Direct report PDF URL from the PSX portal")
    args = parser.parse_args()
    try:
        report_id = ingest_report(args.symbol, args.company, args.period, args.fiscal_year, args.url)
    except (ValueError, httpx.HTTPError, Exception) as exc:
        print(f"Report ingestion failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"Stored report {report_id}; extracted statement text is unreviewed and requires verification.")


if __name__ == "__main__":
    main()
