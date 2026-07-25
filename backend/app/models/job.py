from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("portal", "portal_job_id", name="uq_portal_job_id"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Portal info
    portal: Mapped[str] = mapped_column(String(50), index=True)
    portal_job_id: Mapped[str] = mapped_column(String(255))
    
    # Job details
    title: Mapped[str] = mapped_column(String(500))
    company: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hybrid: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Compensation
    salary_min: Mapped[Optional[int]] = mapped_column(nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(3), default="INR")
    
    # Job details
    job_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # full-time, part-time, contract
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    skills_required: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    
    # URLs
    url: Mapped[str] = mapped_column(String(1000))
    company_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Metadata
    posted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Matching
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_match: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Extra portal-specific data
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
