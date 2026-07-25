from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Profile data
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Skills and experience
    skills: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    experience_years: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    education: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    job_titles: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    
    # Preferences
    preferred_locations: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    remote_preference: Mapped[Optional[str]] = mapped_column(String(20), default="remote")
    desired_salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    desired_salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Resume
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Settings
    auto_apply_threshold: Mapped[Optional[int]] = mapped_column(Integer, default=90)
    search_keywords: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    active_portals: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
