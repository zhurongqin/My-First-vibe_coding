from fastapi import APIRouter
from . import routes
from . import task_routes

api_router = APIRouter()

# Include main upload routes under /upload prefix
api_router.include_router(routes.router, prefix="/upload", tags=["upload"])

# Include task management routes
api_router.include_router(task_routes.router, prefix="/tasks", tags=["tasks"])