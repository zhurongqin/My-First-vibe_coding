from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from typing import Optional
import uuid
from datetime import datetime
import os
from ...config import settings
from ...tasks import remove_background_task
from celery.result import AsyncResult
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片接口
    """
    # 验证文件类型
    allowed_types = settings.ALLOWED_FILE_TYPES
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")
    
    # 读取文件内容以验证大小
    contents = await file.read()
    file_size = len(contents)
    
    # 验证文件大小 (10MB限制)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"文件大小超出限制: {file_size} bytes > {settings.MAX_FILE_SIZE} bytes"
        )
    
    # 重新设置文件指针以供后续使用
    await file.seek(0)
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
    
    # 保存文件到临时目录
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
    
    # 启动异步任务处理图像
    output_filename = f"{file_id}_output.png"
    output_path = os.path.join(settings.OUTPUT_FOLDER, output_filename)
    
    task = remove_background_task.delay(file_path, output_path)
    
    return {
        "filename": file.filename,
        "original_filename": file.filename,
        "stored_filename": filename,
        "content_type": file.content_type,
        "size": file_size,
        "upload_id": file_id,
        "task_id": task.id,  # 添加任务ID
        "output_path": output_path,
        "timestamp": datetime.now().isoformat(),
        "message": "文件上传成功，后台处理中"
    }

@router.get("/status/{task_id}")
async def get_processing_status(task_id: str):
    """
    获取处理状态接口
    """
    task = AsyncResult(task_id, app=remove_background_task.app)
    
    if task.state == 'PENDING':
        # 任务尚未开始
        response = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0,
            "message": "任务正在排队中"
        }
    elif task.state == 'PROGRESS':
        # 任务正在处理中
        response = {
            "task_id": task_id,
            "status": "processing",
            "progress": task.info.get('progress', 50),
            "message": "图像处理中..."
        }
    elif task.state == 'SUCCESS':
        # 任务成功完成
        response = {
            "task_id": task_id,
            "status": "completed",
            "result": task.result,
            "message": "处理完成"
        }
    else:
        # 任务失败或异常
        response = {
            "task_id": task_id,
            "status": "failed",
            "error": str(task.info),
            "message": "处理失败"
        }
    
    return response

@router.get("/result/{task_id}")
async def get_processing_result(task_id: str):
    """
    获取处理结果接口
    """
    task = AsyncResult(task_id, app=remove_background_task.app)
    
    if task.state == 'SUCCESS':
        result = task.result
        return {
            "task_id": task_id,
            "status": "completed",
            "result_data": result,
            "result_url": f"/api/v1/download/{task_id}",
            "message": "处理完成"
        }
    elif task.state in ('PENDING', 'PROGRESS'):
        return {
            "task_id": task_id,
            "status": "processing",
            "message": "图像仍在处理中"
        }
    else:
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(task.info),
            "message": "处理失败"
        }

@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """
    下载处理结果接口
    """
    task = AsyncResult(task_id, app=remove_background_task.app)
    
    if task.state == 'SUCCESS':
        result = task.result
        if result and result.get("status") == "success":
            output_path = result.get("output_path")
            if os.path.exists(output_path):
                # 返回处理后的图像文件
                return FileResponse(
                    path=output_path,
                    media_type='image/png',
                    filename=os.path.basename(output_path)
                )
            else:
                raise HTTPException(status_code=404, detail="处理后的文件未找到")
        else:
            raise HTTPException(status_code=500, detail="任务处理失败")
    else:
        raise HTTPException(status_code=400, detail="任务尚未完成或失败")