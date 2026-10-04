from fastapi import APIRouter

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.meetings import router as meetings_router

router = APIRouter()
router.include_router(health_router)
router.include_router(meetings_router)
