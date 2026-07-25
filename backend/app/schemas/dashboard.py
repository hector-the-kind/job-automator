from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_jobs_scraped: int
    total_applications: int
    discovered: int
    to_apply: int
    applied: int
    screening: int
    interview: int
    completed: int
    offer_count: int
    rejected_count: int
    response_rate: float


class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_applications: list[dict]
    portal_breakdown: dict[str, int]
