from fastapi import APIRouter

from . import routes

api_router = APIRouter()
api_router.include_router(routes.router, prefix="/upload", tags=["upload"])