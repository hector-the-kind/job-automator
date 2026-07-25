from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Any
from pydantic import field_validator
import json


class Settings(BaseSettings):
    APP_NAME: str = "Job Automator"
    # Set DEBUG to True or False
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/job_automator"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/job_automator"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # Scraper settings
    SCRAPE_INTERVAL_HOURS: int = 4
    MATCH_INTERVAL_MINUTES: int = 30
    AUTO_APPLY_THRESHOLD: int = 90
    
    # Location settings
    PRIMARY_LOCATION: str = "Hyderabad"
    ACCEPT_REMOTE_INDIAN: bool = True
    
    # Job search defaults (set to Any so pydantic-settings doesn't force JSON-decoding before validation)
    DEFAULT_KEYWORDS: Any = ["product manager", "builder PM", "product lead"]
    DEFAULT_PORTALS: Any = ["linkedin", "naukri", "wellfound", "cutshort", "iimjobs", "hirect", "foundit", "indeed"]
    
    # User profile
    USER_SKILLS: Any = []
    USER_EXPERIENCE_YEARS: int = 0
    USER_EDUCATION: str = ""
    
    @field_validator("DEFAULT_KEYWORDS", "DEFAULT_PORTALS", "USER_SKILLS", mode="before")
    @classmethod
    def parse_lists(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [item.strip() for item in v_stripped.split(",") if item.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"



@lru_cache()
def get_settings() -> Settings:
    return Settings()
