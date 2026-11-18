from app.api.routes.company_reports import router as company_reports_router
from app.api.routes.health import router as health_router
from app.api.routes.indicators import router as indicators_router

__all__ = ["company_reports_router", "health_router", "indicators_router"]
