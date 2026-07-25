from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApplicationBase(BaseModel):
    user_id: int
    job_id: int
    match_score: float
    auto_applied: bool = False


class ApplicationCreate(ApplicationBase):
    status: str = "discovered"


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    outcome: Optional[str] = None
    offer_salary: Optional[int] = None


class ApplicationResponse(ApplicationBase):
    id: int
    status: str
    applied_at: Optional[datetime] = None
    portal_application_id: Optional[str] = None
    cover_letter_used: Optional[str] = None
    custom_answers: Optional[dict] = {}
    interview_date: Optional[datetime] = None
    outcome: Optional[str] = None
    offer_salary: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    applications: list[ApplicationResponse]
    total: int
