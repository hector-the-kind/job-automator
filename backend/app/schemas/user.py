from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    skills: Optional[list[str]] = None
    experience_years: Optional[int] = None
    education: Optional[list[dict]] = None
    job_titles: Optional[list[str]] = None
    preferred_locations: Optional[list[str]] = None
    remote_preference: Optional[str] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    resume_text: Optional[str] = None
    auto_apply_threshold: Optional[int] = None
    search_keywords: Optional[list[str]] = None
    active_portals: Optional[list[str]] = None


class UserResponse(UserBase):
    id: int
    skills: Optional[list[str]] = []
    experience_years: Optional[int] = 0
    education: Optional[list[dict]] = []
    job_titles: Optional[list[str]] = []
    preferred_locations: Optional[list[str]] = []
    remote_preference: Optional[str] = "remote"
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    auto_apply_threshold: Optional[int] = 90
    search_keywords: Optional[list[str]] = []
    active_portals: Optional[list[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
