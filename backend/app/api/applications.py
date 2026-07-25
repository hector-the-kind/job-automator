from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.application import Application
from app.models.job import Job
from app.schemas.application import ApplicationResponse, ApplicationListResponse, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=ApplicationListResponse)
async def list_applications(
    status: str = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Application)
    
    if status:
        query = query.where(Application.status == status)
    
    query = query.order_by(Application.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    count_query = select(func.count(Application.id))
    if status:
        count_query = count_query.where(Application.status == status)
    
    total = (await db.execute(count_query)).scalar() or 0
    
    return ApplicationListResponse(
        applications=[ApplicationResponse.model_validate(app) for app in applications],
        total=total
    )



@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return ApplicationResponse.model_validate(app)


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int,
    update: ApplicationUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(app, key, value)
    
    await db.commit()
    await db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.post("/{application_id}/approve", response_model=ApplicationResponse)
async def approve_application(application_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if app.status != "discovered":
        raise HTTPException(status_code=400, detail="Application is not in discovered status")
    
    app.status = "to_apply"
    await db.commit()
    await db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.post("/{application_id}/decline", response_model=ApplicationResponse)
async def decline_application(application_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = "completed"
    app.outcome = "withdrawn"
    await db.commit()
    await db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.get("/stats/summary")
async def get_application_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Application.status,
            func.count(Application.id)
        ).group_by(Application.status)
    )
    stats = {row[0]: row[1] for row in result.all()}
    
    total = sum(stats.values())
    
    return {
        "total": total,
        "discovered": stats.get("discovered", 0),
        "to_apply": stats.get("to_apply", 0),
        "applied": stats.get("applied", 0),
        "screening": stats.get("screening", 0),
        "interview": stats.get("interview", 0),
        "completed": stats.get("completed", 0),
        "offer_count": stats.get("offer", 0),
        "rejected_count": stats.get("rejected", 0),
    }
