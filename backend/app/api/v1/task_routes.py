from fastapi import APIRouter, HTTPException
from ...tasks import remove_background_task, cleanup_old_files
from celery.result import AsyncResult
from fastapi.responses import FileResponse
import os
from ...config import settings

router = APIRouter()

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

@router.post("/cleanup")
async def trigger_cleanup():
    """
    手动触发文件清理任务
    """
    task = cleanup_old_files.delay()
    return {
        "message": "文件清理任务已启动",
        "task_id": task.id
    }