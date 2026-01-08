from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .config import settings
from .api.v1 import api_router
import logging
from .rate_limit import check_rate_limit

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="图像背景移除API", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应更具体地设置允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    限流中间件，应用于所有请求
    """
    # 对特定路径跳过限流
    if request.url.path not in ["/health", "/docs", "/redoc", f"{settings.API_V1_STR}/upload"]:
        response = await call_next(request)
        return response
    
    # 对上传接口应用限流
    if request.url.path == f"{settings.API_V1_STR}/upload":
        check_rate_limit(request, max_requests=60, window=60)  # 60次/分钟
    
    response = await call_next(request)
    return response

# 包含API路由
app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
    tags=["image-processing"]
)

@app.get("/")
async def root():
    """
    根路径，返回API服务信息
    """
    return {"message": "图像背景移除API服务运行中", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """
    健康检查端点，验证API服务状态
    """
    return {"status": "healthy", "version": "1.0.0", "timestamp": __import__('datetime').datetime.now()}

# 错误处理机制
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证错误
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    
    logger.error(f"Validation error: {exc}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "输入验证失败",
            "details": errors
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理一般性错误
    """
    logger.error(f"General exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "details": str(exc) if settings.PORT != 80 else "发生未知错误"
        }
    )

# 确保上传和输出目录存在
import os
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.OUTPUT_FOLDER, exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)