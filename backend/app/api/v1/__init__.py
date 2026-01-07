from fastapi import APIRouter

from . import routes
from . import task_routes

api_router = APIRouter()

# 只将上传相关路由放在/upload下
api_router.include_router(routes.router, prefix="/upload", tags=["upload"])

# 将任务相关路由（状态、结果、下载）直接添加到api/v1下
api_router.include_router(task_routes.router, tags=["task"])
