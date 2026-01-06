from celery import Celery

# Celery配置
celery_app = Celery('image_bg_remove')

celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=False,
    task_routes={
        'app.tasks.remove_background': {'queue': 'background_removal'}
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)