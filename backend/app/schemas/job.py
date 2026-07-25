from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class JobBase(BaseModel):
    portal: str
    portal_job_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool = False
    is_hybrid: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "INR"
    job_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[list[str]] = []
    skills_required: Optional[list[str]] = []
    url: str
    company_url: Optional[str] = None
    posted_at: Optional[datetime] = None


class JobCreate(JobBase):
    match_score: Optional[float] = None
    location_match: bool = True
    metadata: Optional[dict] = {}


class JobResponse(JobBase):
    id: int
    match_score: Optional[float] = None
    location_match: bool
    scraped_at: datetime
    is_active: bool
    metadata: Optional[dict] = {}

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    per_page: int
