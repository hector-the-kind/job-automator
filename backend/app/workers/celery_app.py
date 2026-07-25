from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "job_automator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    "scrape-score-apply-every-4-hours": {
        "task": "app.workers.scrape_jobs.run_all_scrapers",
        "schedule": crontab(hour="*/4", minute=0),
    },
    "send-telegram-notifications-every-30-minutes": {
        "task": "app.workers.match_and_apply.process_new_jobs",
        "schedule": crontab(minute="*/30"),
    },
    "check-application-status-daily": {
        "task": "app.workers.check_status.update_application_statuses",
        "schedule": crontab(hour=9, minute=0),
    },
}
