from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


async def get_user_profile(db: AsyncSession) -> User | None:
    """Get the single user profile."""
    result = await db.execute(select(User).limit(1))
    return result.scalar_one_or_none()


async def create_or_update_profile(db: AsyncSession, profile_data: dict) -> User:
    """Create or update the user profile."""
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(**profile_data)
        db.add(user)
    else:
        for key, value in profile_data.items():
            if value is not None:
                setattr(user, key, value)
    
    return user


async def get_matchable_profile(db: AsyncSession) -> tuple[dict, str]:
    """Get profile formatted for matching engine."""
    user = await get_user_profile(db)
    
    if not user:
        return {}, ""
    
    profile = {
        "skills": user.skills or [],
        "experience_years": user.experience_years or 0,
        "job_titles": user.job_titles or [],
        "preferred_locations": user.preferred_locations or [],
        "remote_preference": user.remote_preference or "remote",
        "auto_apply_threshold": user.auto_apply_threshold or 90,
    }
    
    resume_text = user.resume_text or ""
    
    return profile, resume_text
