from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    HealthResponse,
    StatusResponse,
    VerdictListResponse,
    VerdictListItem,
    VerdictResponse,
)
from app.database import check_db_health, get_db
from app.models import Analysis, Verdict, Source
from app.services.analysis import create_analysis

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    from redis import Redis
    from app.config import settings

    db_ok = check_db_health()
    try:
        r = Redis.from_url(settings.redis_url)
        r.ping()
        queue_ok = True
    except Exception:
        queue_ok = False

    status = "ok" if db_ok and queue_ok else "degraded"
    return HealthResponse(
        status=status,
        db="ok" if db_ok else "error",
        queue="ok" if queue_ok else "error",
    )


@router.post("/analysis", response_model=AnalysisResponse, status_code=201)
def submit_analysis(req: AnalysisRequest, db: Session = Depends(get_db)):
    analysis = create_analysis(db, req.input_type, req.content)
    return AnalysisResponse(
        job_id=analysis.id, slug=analysis.slug, status=analysis.status
    )


@router.get("/analysis/{job_id}/status", response_model=StatusResponse)
def get_analysis_status(job_id: UUID, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == job_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    progress_step = None
    if analysis.status == "processing":
        # Check Celery task meta for progress step
        from app.worker import celery_app

        result = celery_app.AsyncResult(str(analysis.id))
        if result.info and isinstance(result.info, dict):
            progress_step = result.info.get("step")

    return StatusResponse(
        status=analysis.status,
        progress_step=progress_step,
        slug=analysis.slug if analysis.status == "complete" else None,
    )


@router.get("/verdict/{slug}", response_model=VerdictResponse)
def get_verdict(slug: str, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.slug == slug).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Verdict not found")
    if analysis.status != "complete":
        raise HTTPException(status_code=404, detail="Verdict not ready yet")

    verdict = analysis.verdict
    if not verdict:
        raise HTTPException(status_code=404, detail="Verdict not found")

    return VerdictResponse(
        slug=analysis.slug,
        policy_text=analysis.policy_text,
        verdict=verdict.verdict,
        confidence=verdict.confidence,
        studies_used=verdict.studies_used,
        summary=verdict.summary,
        evidence_for=verdict.evidence_for,
        evidence_against=verdict.evidence_against,
        created_at=verdict.created_at,
    )


@router.get("/verdicts", response_model=VerdictListResponse)
def list_verdicts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Analysis)
        .filter(Analysis.status == "complete")
        .order_by(Analysis.created_at.desc())
    )
    total = query.count()
    analyses = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for a in analyses:
        if a.verdict:
            items.append(
                VerdictListItem(
                    slug=a.slug,
                    verdict=a.verdict.verdict,
                    confidence=a.verdict.confidence,
                    studies_used=a.verdict.studies_used,
                    summary=a.verdict.summary,
                    created_at=a.verdict.created_at,
                )
            )

    return VerdictListResponse(
        items=items, total=total, page=page, page_size=page_size
    )
