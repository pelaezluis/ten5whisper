from celery import Celery
from app.core.config import settings
import os

celery = Celery('task')
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")


class CeleryConfig:
    task_serializer = "pickle"
    result_serializer = "pickle"
    event_serializer = "json"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_accept_content = ["application/json", "application/x-python-serialize"]

celery.config_from_object(CeleryConfig)

celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.autodiscover_tasks()

from app.api.celery_task import *
