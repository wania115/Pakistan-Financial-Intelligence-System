from app.api.routes.health import router as health_router
from app.api.routes.indicators import router as indicators_router

__all__ = ["health_router", "indicators_router"]
