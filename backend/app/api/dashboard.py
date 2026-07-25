from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.job import Job
from app.models.application import Application
from app.schemas.dashboard import DashboardStats, DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # Total jobs scraped
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar() or 0
    
    # Application counts by status
    result = await db.execute(
        select(
            Application.status,
            func.count(Application.id)
        ).group_by(Application.status)
    )
    status_counts = {row[0]: row[1] for row in result.all()}
    
    total_apps = sum(status_counts.values())
    applied = status_counts.get("applied", 0)
    screening = status_counts.get("screening", 0)
    interview = status_counts.get("interview", 0)
    completed = status_counts.get("completed", 0)
    
    # Response rate (screening + interview + completed) / total applied
    responded = screening + interview + completed
    response_rate = (responded / applied * 100) if applied > 0 else 0.0
    
    return DashboardStats(
        total_jobs_scraped=total_jobs,
        total_applications=total_apps,
        discovered=status_counts.get("discovered", 0),
        to_apply=status_counts.get("to_apply", 0),
        applied=applied,
        screening=screening,
        interview=interview,
        completed=completed,
        offer_count=status_counts.get("offer", 0),
        rejected_count=status_counts.get("rejected", 0),
        response_rate=round(response_rate, 1)
    )


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    stats = await get_dashboard_stats(db)
    
    # Recent applications
    result = await db.execute(
        select(Application).order_by(Application.created_at.desc()).limit(10)
    )
    recent_apps = result.scalars().all()
    
    # Portal breakdown
    portal_result = await db.execute(
        select(Job.portal, func.count(Job.id)).group_by(Job.portal)
    )
    portal_breakdown = {row[0]: row[1] for row in portal_result.all()}
    
    return DashboardResponse(
        stats=stats,
        recent_applications=[
            {
                "id": app.id,
                "status": app.status,
                "match_score": app.match_score,
                "created_at": app.created_at.isoformat(),
            }
            for app in recent_apps
        ],
        portal_breakdown=portal_breakdown
    )
