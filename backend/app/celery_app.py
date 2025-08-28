# celery_app.py
from celery import Celery
import os

celery_app = Celery(
    "log_worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)
celery_app.conf.task_routes = {
    "app.tasks.process_log_task": {"queue": "logs"}
}

from . import tasks