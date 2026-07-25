from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=UserResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        # Create default user
        user = User(
            full_name="Job Seeker",
            search_keywords=["product manager", "builder PM"],
            active_portals=["linkedin", "naukri", "wellfound", "cutshort", "iimjobs", "hirect", "foundit", "indeed"],
            preferred_locations=["Hyderabad", "Remote"]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/", response_model=UserResponse)
async def update_profile(
    update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)
