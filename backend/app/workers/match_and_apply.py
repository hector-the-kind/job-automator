import logging
from celery import shared_task
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@shared_task(name="app.workers.match_and_apply.process_new_jobs")
def process_new_jobs():
    """Process the to_apply queue: send Telegram notifications for discovered jobs."""
    from app.database import async_session
    from app.services.job_service import get_jobs_for_notification
    from app.bot.telegram_bot import send_notification_direct

    async def _process():
        from sqlalchemy import select
        from app.models.user import User

        async with async_session() as db:
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            chat_id = user.telegram_chat_id if user else ""

            pending_jobs = await get_jobs_for_notification(db, status="discovered")

            sent = 0
            for item in pending_jobs:
                try:
                    await send_notification_direct(
                        chat_id=chat_id,
                        job=item["job"],
                        score=item["score"],
                        app_id=item["application_id"],
                    )
                    sent += 1
                except Exception as e:
                    logger.error(f"Failed to send notification: {e}")

            return {"pending": len(pending_jobs), "sent": sent}

    return run_async(_process())


@shared_task(name="app.workers.match_and_apply.send_approval_notifications")
def send_approval_notifications():
    """Alias for process_new_jobs — kept for backwards compat."""
    return process_new_jobs.apply()


def run_async(coro):
    """Run async function in Celery task."""
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
