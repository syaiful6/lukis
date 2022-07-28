from fastapi import APIRouter
from .render import render_router


v1_api = APIRouter()

v1_api.include_router(render_router, prefix="/render")