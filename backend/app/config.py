import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 服务配置
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))
    API_V1_STR: str = os.getenv('API_V1_STR', '/api/v1')
    
    # Redis配置
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    
    # 文件上传配置
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB
    ALLOWED_FILE_TYPES: list = [
        'image/jpeg', 
        'image/jpg', 
        'image/png', 
        'image/webp', 
        'image/bmp'
    ]
    
    # 本地存储配置
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', './uploads')
    OUTPUT_FOLDER: str = os.getenv('OUTPUT_FOLDER', './outputs')
    
    # API配置
    EXTERNAL_API_URL: str = os.getenv('EXTERNAL_API_URL', 'http://115.159.43.168:5000/api/remove-bg/base64')
    
    # 图像压缩配置
    COMPRESS_QUALITY: int = int(os.getenv('COMPRESS_QUALITY', 85))  # JPEG质量，1-100
    COMPRESS_MAX_WIDTH: int = int(os.getenv('COMPRESS_MAX_WIDTH', 1920))  # 最大宽度
    COMPRESS_MAX_HEIGHT: int = int(os.getenv('COMPRESS_MAX_HEIGHT', 1080))  # 最大高度
    
    # 任务重试配置
    TASK_MAX_RETRIES: int = int(os.getenv('TASK_MAX_RETRIES', 3))
    
    # Celery配置
    @property
    def redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# 创建全局配置实例
settings = Settings()