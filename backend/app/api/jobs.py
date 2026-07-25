from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobListResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    portal: str = Query(None, description="Filter by portal"),
    min_score: float = Query(None, description="Minimum match score"),
    is_active: bool = Query(True, description="Filter active jobs"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Job).where(Job.is_active == is_active)
    
    if portal:
        query = query.where(Job.portal == portal)
    if min_score is not None:
        query = query.where(Job.match_score >= min_score)
    
    query = query.order_by(Job.match_score.desc().nullslast(), Job.scraped_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    count_query = select(func.count(Job.id)).where(Job.is_active == is_active)
    if portal:
        count_query = count_query.where(Job.portal == portal)
    if min_score is not None:
        count_query = count_query.where(Job.match_score >= min_score)
    
    total = (await db.execute(count_query)).scalar() or 0
    
    return JobListResponse(
        jobs=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)
