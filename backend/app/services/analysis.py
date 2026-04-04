from slugify import slugify
from sqlalchemy.orm import Session

from app.models import Analysis
from app.services.tasks import run_analysis_pipeline


def create_analysis(db: Session, input_type: str, content: str) -> Analysis:
    # For text input, use directly. URL/PDF extraction happens in the worker.
    policy_text = content if input_type == "text" else ""

    slug = _generate_slug(db, content[:80])

    analysis = Analysis(
        slug=slug,
        input_type=input_type,
        input_raw=content if input_type != "text" else None,
        policy_text=policy_text if policy_text else "pending extraction",
        status="pending",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Dispatch async task
    run_analysis_pipeline.apply_async(
        args=[str(analysis.id)],
        task_id=str(analysis.id),
    )

    return analysis


def _generate_slug(db: Session, text: str) -> str:
    base_slug = slugify(text, max_length=60)
    if not base_slug:
        base_slug = "analysis"

    slug = base_slug
    counter = 1
    while db.query(Analysis).filter(Analysis.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
