from celery import Celery

from app.config import settings

celery_app = Celery(
    "goveval",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=180,  # 3 min hard limit
    task_soft_time_limit=150,  # 2.5 min soft limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Import tasks so Celery discovers them
celery_app.autodiscover_tasks(["app.services"])
