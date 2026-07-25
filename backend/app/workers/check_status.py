import logging
from celery import shared_task
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def run_async(coro):
    """Run async function in Celery task."""
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(name="app.workers.check_status.update_application_statuses")
def update_application_statuses():
    """
    Check application statuses on portals and update DB.
    Since portal login is not configured, this uses time-based heuristics:
    - Applications older than 3 days in 'applied' → move to 'screening'
    - Applications older than 7 days in 'screening' → move to 'completed' (rejected)
    """
    from datetime import datetime, timedelta
    from sqlalchemy import select
    from app.database import async_session
    from app.models.application import Application

    async def _check():
        updated = 0
        async with async_session() as db:
            now = datetime.utcnow()

            # Move applied → screening after 3 days
            applied_cutoff = now - timedelta(days=3)
            result = await db.execute(
                select(Application).where(
                    Application.status == "applied",
                    Application.applied_at < applied_cutoff,
                )
            )
            for app in result.scalars().all():
                app.status = "screening"
                updated += 1
                logger.info(f"Application {app.id}: applied → screening")

            # Move screening → completed (rejected) after 14 days
            screening_cutoff = now - timedelta(days=14)
            result = await db.execute(
                select(Application).where(
                    Application.status == "screening",
                    Application.updated_at < screening_cutoff,
                )
            )
            for app in result.scalars().all():
                app.status = "completed"
                app.outcome = "rejected"
                updated += 1
                logger.info(f"Application {app.id}: screening → completed (rejected)")

            await db.commit()

        return {"updated": updated}

    return run_async(_check())
