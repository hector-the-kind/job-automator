import asyncio
import logging
from celery import shared_task
from app.config import get_settings
from app.scrapers.linkedin import LinkedInScraper
from app.scrapers.naukri import NaukriScraper
from app.scrapers.wellfound import WellfoundScraper

logger = logging.getLogger(__name__)
settings = get_settings()


def run_async(coro):
    """Run async function in Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def scrape_all_portals(keywords: list[str], location: str = "Hyderabad") -> list[dict]:
    """Scrape jobs from all configured portals."""
    all_jobs = []

    scrapers = {
        "linkedin": LinkedInScraper(),
        "naukri": NaukriScraper(),
        "wellfound": WellfoundScraper(),
    }

    for portal_name, scraper in scrapers.items():
        if portal_name not in settings.DEFAULT_PORTALS:
            continue

        try:
            for keyword in keywords:
                logger.info(f"[{portal_name}] Searching for: {keyword}")
                jobs = await scraper.scrape(keyword, location, max_pages=2)
                all_jobs.extend(jobs)
                logger.info(f"[{portal_name}] Found {len(jobs)} jobs for '{keyword}'")
        except Exception as e:
            logger.error(f"[{portal_name}] Error: {e}")
        finally:
            await scraper.close()

    return all_jobs


@shared_task(name="app.workers.scrape_jobs.run_all_scrapers")
def run_all_scrapers():
    """Scrape all portals, store jobs, score them, and create applications."""
    from app.database import async_session
    from app.models.user import User
    from app.services.job_service import process_new_job

    async def _scrape_and_process():
        from sqlalchemy import select

        async with async_session() as db:
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()

            if not user:
                logger.warning("No user profile found")
                return {"processed": 0}

            user_profile = {
                "skills": user.skills or [],
                "experience_years": user.experience_years or 0,
                "job_titles": user.job_titles or [],
                "preferred_locations": user.preferred_locations or [],
                "remote_preference": user.remote_preference or "remote",
                "auto_apply_threshold": user.auto_apply_threshold or 90,
            }
            resume_text = user.resume_text or ""
            keywords = user.search_keywords or settings.DEFAULT_KEYWORDS

            jobs = await scrape_all_portals(keywords, settings.PRIMARY_LOCATION)

            processed = 0
            auto_applied = 0
            pending_approval = 0

            for job_data in jobs:
                try:
                    app = await process_new_job(db, job_data, user_profile, resume_text)
                    if app:
                        processed += 1
                        if app.auto_applied:
                            auto_applied += 1
                        else:
                            pending_approval += 1
                except Exception as e:
                    logger.error(f"Error processing job: {e}")

            await db.commit()

            return {
                "total_scraped": len(jobs),
                "processed": processed,
                "auto_applied": auto_applied,
                "pending_approval": pending_approval,
            }

    return run_async(_scrape_and_process())
