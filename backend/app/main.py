from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.api import health_router, indicators_router
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Indicator


INDICATOR_CATALOG = [
    {
        "code": "KIBOR",
        "name": "KIBOR",
        "category": "Interest rates",
        "unit": "%",
        "frequency": "Business day",
        "description": "Karachi Interbank Offered Rate. Tenor-specific values will be represented as separate series in a later iteration.",
    },
    {
        "code": "CPI_INFLATION",
        "name": "Consumer price inflation",
        "category": "Prices",
        "unit": "% year-over-year",
        "frequency": "Monthly",
        "description": "Consumer price inflation rate; geographic and category breakdowns can be added as separate series.",
    },
    {
        "code": "USD_PKR",
        "name": "USD / PKR exchange rate",
        "category": "Foreign exchange",
        "unit": "PKR per USD",
        "frequency": "Daily",
        "description": "Pakistani rupees per US dollar. The exchange-rate series definition should identify its specific source and convention.",
    },
    {
        "code": "SBP_POLICY_RATE",
        "name": "SBP policy rate",
        "category": "Interest rates",
        "unit": "%",
        "frequency": "Policy announcement",
        "description": "State Bank of Pakistan policy rate, recorded by effective date.",
    },
    {
        "code": "TBILL_3M_YIELD",
        "name": "3-month Treasury bill yield",
        "category": "Government securities",
        "unit": "%",
        "frequency": "Auction",
        "description": "Three-month Treasury bill auction yield. Auction measure and dates should be confirmed during ingestion design.",
    },
    {
        "code": "PIB_10Y_YIELD",
        "name": "10-year Pakistan Investment Bond yield",
        "category": "Government securities",
        "unit": "%",
        "frequency": "Auction",
        "description": "Ten-year Pakistan Investment Bond yield. Auction measure and dates should be confirmed during ingestion design.",
    },
]

app = FastAPI(title=settings.app_name, debug=settings.debug, version="0.1.0")
app.include_router(health_router)
app.include_router(indicators_router)
static_dir = __import__("pathlib").Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for item in INDICATOR_CATALOG:
            existing = db.scalar(select(Indicator).where(Indicator.code == item["code"]))
            if existing is None:
                db.add(Indicator(**item))
        db.commit()


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(static_dir / "index.html")
