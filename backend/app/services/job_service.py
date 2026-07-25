from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job import Job
from app.models.application import Application
from app.matching.engine import MatchEngine


async def process_new_job(db: AsyncSession, job_data: dict, user_profile: dict, resume_text: str) -> Application | None:
    """
    Process a newly scraped job: check for duplicates, score it, create application.
    Returns the Application if created, None if duplicate.
    """
    # Check if job already exists
    existing = await db.execute(
        select(Job).where(
            Job.portal == job_data["portal"],
            Job.portal_job_id == job_data["portal_job_id"]
        )
    )
    if existing.scalar_one_or_none():
        return None
    
    # Create job record
    job = Job(
        portal=job_data["portal"],
        portal_job_id=job_data["portal_job_id"],
        title=job_data["title"],
        company=job_data.get("company"),
        location=job_data.get("location"),
        is_remote=job_data.get("is_remote", False),
        is_hybrid=job_data.get("is_hybrid", False),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        salary_currency=job_data.get("salary_currency", "INR"),
        job_type=job_data.get("job_type"),
        description=job_data.get("description"),
        requirements=job_data.get("requirements", []),
        skills_required=job_data.get("skills_required", []),
        url=job_data["url"],
        company_url=job_data.get("company_url"),
        posted_at=job_data.get("posted_at"),
        metadata=job_data.get("metadata", {}),
    )
    db.add(job)
    await db.flush()
    
    # Calculate match score
    engine = MatchEngine(user_profile, resume_text)
    score, location_match = engine.score(job_data)
    
    job.match_score = score
    job.location_match = location_match
    
    # Create application record
    auto_apply = score >= user_profile.get("auto_apply_threshold", 90)
    
    application = Application(
        user_id=1,  # Single user for now
        job_id=job.id,
        match_score=score,
        auto_applied=auto_apply,
        status="to_apply" if auto_apply else "discovered",
    )
    db.add(application)
    
    return application


async def get_jobs_for_notification(db: AsyncSession, status: str = "discovered") -> list[dict]:
    """Get jobs that need to be sent to Telegram for approval."""
    result = await db.execute(
        select(Application, Job)
        .join(Job, Application.job_id == Job.id)
        .where(Application.status == status)
        .order_by(Application.match_score.desc())
        .limit(10)
    )
    
    jobs = []
    for app, job in result.all():
        jobs.append({
            "application_id": app.id,
            "job": {
                "id": job.id,
                "portal": job.portal,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "is_remote": job.is_remote,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "url": job.url,
            },
            "score": app.match_score,
        })
    
    return jobs
