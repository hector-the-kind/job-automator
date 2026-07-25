from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    
    # Status tracking
    # Status flow: discovered -> to_apply -> applied -> screening -> interview -> completed
    status: Mapped[str] = mapped_column(String(30), default="discovered", index=True)
    # discovered: New match from scraper
    # to_apply: Approved (manually or auto), queued for submission
    # applied: Application sent to portal
    # screening: Company reviewing application
    # interview: Interview scheduled/in progress
    # completed: Offer received OR rejected/withdrawn
    
    # Application details
    match_score: Mapped[float] = mapped_column(Float)
    auto_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # Portal tracking
    portal_application_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cover_letter_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_answers: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Outcome
    interview_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # offer, rejected, withdrawn
    offer_salary: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
