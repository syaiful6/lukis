from fastapi import APIRouter

from .v1.router import v1_api

router = APIRouter()

router.include_router(v1_api, prefix="/v1")