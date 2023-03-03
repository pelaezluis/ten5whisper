from fastapi import APIRouter
from app.api.endpoints import translate
router = APIRouter()

router.include_router(translate.router, prefix='/api/v1/translate')