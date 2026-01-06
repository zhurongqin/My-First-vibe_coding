import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 服务配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    API_V1_STR: str = "/api/v1"
    
    # Redis配置 (用于Celery)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # 文件上传配置
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    ALLOWED_FILE_TYPES: list = [
        "image/jpeg", 
        "image/jpg", 
        "image/png", 
        "image/webp", 
        "image/bmp"
    ]
    
    # 本地存储配置
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    OUTPUT_FOLDER: str = os.getenv("OUTPUT_FOLDER", "./outputs")
    
    # API配置
    EXTERNAL_API_TIMEOUT: int = int(os.getenv("EXTERNAL_API_TIMEOUT", "300"))  # 5分钟超时
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "60/minute")  # 限流配置
    
    class Config:
        env_file = ".env"

# 创建全局配置实例
settings = Settings()