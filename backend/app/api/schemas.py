from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    input_type: str = Field(pattern="^(text|url|pdf)$")
    content: str = Field(min_length=1, max_length=100_000)


class AnalysisResponse(BaseModel):
    job_id: UUID
    slug: str
    status: str


class StatusResponse(BaseModel):
    status: str
    progress_step: Optional[str] = None
    slug: Optional[str] = None


class EvidenceItem(BaseModel):
    claim: str
    doi: Optional[str] = None
    title: str


class VerdictResponse(BaseModel):
    slug: str
    policy_text: str
    verdict: str
    confidence: int
    studies_used: int
    summary: str
    evidence_for: list[EvidenceItem]
    evidence_against: list[EvidenceItem]
    created_at: datetime


class VerdictListItem(BaseModel):
    slug: str
    verdict: str
    confidence: int
    studies_used: int
    summary: str
    created_at: datetime


class VerdictListResponse(BaseModel):
    items: list[VerdictListItem]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    status: str
    db: str
    queue: str
