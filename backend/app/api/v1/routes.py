from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from ...tasks import remove_background_task
from ...config import settings
import uuid
import os
import time
from typing import Dict, Any

router = APIRouter()

# 简单的内存缓存实现（生产环境建议使用Redis）
cache: Dict[str, Any] = {}
CACHE_TIMEOUT = 300  # 5分钟缓存过期时间


def is_cached(file_content: bytes) -> str:
    """检查文件内容是否已在缓存中"""
    file_hash = hash(file_content)
    if file_hash in cache:
        cached_item = cache[file_hash]
        if time.time() - cached_item['timestamp'] < CACHE_TIMEOUT:
            return cached_item['result']
        else:
            # 缓存过期，删除它
            del cache[file_hash]
    return None


def cache_result(file_content: bytes, result: Any):
    """将结果缓存"""
    file_hash = hash(file_content)
    cache[file_hash] = {
        'result': result,
        'timestamp': time.time()
    }


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图像并开始背景移除任务
    """
    # 检查文件类型
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        return JSONResponse(
            status_code=400,
            content={
                "error": "不支持的文件类型",
                "supported_types": settings.ALLOWED_FILE_TYPES
            }
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 检查文件大小
    if len(file_content) > settings.MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"文件大小超过限制 ({settings.MAX_FILE_SIZE / (1024*1024):.1f}MB)",
                "file_size": len(file_content)
            }
        )
    
    # 检查缓存
    cached_result = is_cached(file_content)
    if cached_result:
        return {
            "message": "使用缓存结果",
            "task_id": cached_result.get('task_id'),
            "cached": True
        }
    
    # 生成唯一ID
    file_id = str(uuid.uuid4())
    
    # 创建上传目录（如果不存在）
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    
    # 保存上传的文件
    input_path = os.path.join(settings.UPLOAD_FOLDER, f"{file_id}_{file.filename}")
    with open(input_path, 'wb') as f:
        f.write(file_content)
    
    # 创建输出目录
    os.makedirs(settings.OUTPUT_FOLDER, exist_ok=True)
    
    # 生成输出文件路径
    output_path = os.path.join(settings.OUTPUT_FOLDER, f"{file_id}_output.png")
    
    # 启动异步任务
    task = remove_background_task.delay(input_path, output_path)
    
    # 缓存任务ID
    cache_result(file_content, {"task_id": task.id})
    
    # 返回任务ID
    return {
        "filename": file.filename,
        "file_id": file_id,
        "task_id": task.id,
        "message": "图像上传成功，正在处理中"
    }
