import os
import uuid
from celery import Celery
from PIL import Image
import requests
import base64
from io import BytesIO
import time

from .celery_config import celery_app
from .config import settings

# 示例任务 - 图像背景移除
@celery_app.task(bind=True, max_retries=3)
def remove_background_task(self, image_path, output_path):
    """
    异步执行图像背景移除任务
    """
    try:
        # 读取图像文件
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 将图像数据编码为base64
        encoded_string = base64.b64encode(image_data).decode()
        
        # 调用外部抠图API
        api_url = "http://115.159.43.168:5000/api/remove-bg/base64"  # 根据API文档设置
        
        payload = {
            "base64_str": encoded_string
        }
        
        response = requests.post(
            api_url,
            json=payload,
            timeout=settings.EXTERNAL_API_TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"API调用失败，状态码: {response.status_code}, 响应: {response.text}")
        
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"API返回错误: {result.get('msg')}")
        
        # 获取处理后的图像base64数据
        image_base64 = result.get("image_base64", "")
        if not image_base64:
            raise Exception("API未返回有效的图像数据")
        
        # 解码并保存处理后的图像
        image_data = base64.b64decode(image_base64.split(",")[1] if "," in image_base64 else image_base64)
        
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        return {
            "status": "success", 
            "output_path": output_path,
            "unique_name": result.get("unique_name", ""),
            "message": result.get("msg", "处理完成")
        }
    except Exception as exc:
        # 获取当前重试次数
        retry_count = self.request.retries
        # 计算下次重试的延迟时间（递增：1秒、3秒、5秒）
        countdown = min(5, 2 * retry_count + 1)  # 1, 3, 5秒
        
        # 记录错误信息
        print(f"任务执行失败，将进行第{retry_count + 1}次重试，延迟{countdown}秒: {str(exc)}")
        
        # 发生错误时重试（最多3次，递增延迟）
        if retry_count < self.max_retries:
            raise self.retry(exc=exc, countdown=countdown)
        else:
            # 重试次数已达上限
            return {
                "status": "failed",
                "error": str(exc),
                "message": f"任务执行失败，已重试{self.max_retries}次"
            }