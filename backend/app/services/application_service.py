from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.application import Application
from app.models.job import Job


async def approve_application(db: AsyncSession, application_id: int) -> Application | None:
    """Approve an application for submission."""
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app or app.status != "discovered":
        return None
    
    app.status = "to_apply"
    return app


async def decline_application(db: AsyncSession, application_id: int) -> Application | None:
    """Decline/withdraw an application."""
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        return None
    
    app.status = "completed"
    app.outcome = "withdrawn"
    return app


async def mark_applied(db: AsyncSession, application_id: int) -> Application | None:
    """Mark application as submitted."""
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app or app.status != "to_apply":
        return None
    
    app.status = "applied"
    app.applied_at = datetime.utcnow()
    return app


async def update_status(db: AsyncSession, application_id: int, new_status: str) -> Application | None:
    """Update application status."""
    valid_transitions = {
        "discovered": ["to_apply", "completed"],
        "to_apply": ["applied", "completed"],
        "applied": ["screening", "completed"],
        "screening": ["interview", "completed"],
        "interview": ["completed"],
        "completed": [],
    }
    
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        return None
    
    if new_status not in valid_transitions.get(app.status, []):
        return None
    
    app.status = new_status
    return app
