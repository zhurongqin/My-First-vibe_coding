import os
from celery import Celery
from .config import settings

# 创建Celery实例，使用Redis作为broker和backend
celery_app = Celery(
    "image_bg_remove",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks']  # 明确包含任务模块
)

# 配置Celery
celery_app.config_from_object({
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'result_expires': 3600,  # 结果过期时间
    'task_routes': {
        # 移除特定队列路由，让任务使用默认队列
    },
    'worker_prefetch_multiplier': 1,
    'task_acks_late': True,
}, namespace='CELERY')

if __name__ == '__main__':
    celery_app.start()