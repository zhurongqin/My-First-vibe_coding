from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: Exception):
    """
    HTTP异常处理
    """
    logger.error(f"HTTP Exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理
    """
    logger.error(f"Validation error: {exc}")
    errors = []
    for error in exc.errors():
        field = str(error["loc"][-1])
        message = error["msg"]
        errors.append({"field": field, "message": message})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "输入数据验证失败",
            "errors": errors
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    一般异常处理
    """
    logger.error(f"General exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error": str(exc)
        }
    )

# 创建一个错误响应的通用函数
def create_error_response(message: str, status_code: int = 400, details: dict = None):
    """
    创建错误响应
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "details": details or {}
        }
    )

# 创建一个成功响应的通用函数
def create_success_response(data: dict = None, message: str = "Success"):
    """
    创建成功响应
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": message,
            "data": data or {}
        }
    )