import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Verdict(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "verdicts"

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False
    )
    verdict: Mapped[str] = mapped_column(Text, nullable=False)  # smart | mixed | poor
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    studies_used: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_for: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    evidence_against: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    raw_llm_output: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_confidence_range"),
    )

    analysis = relationship("Analysis", back_populates="verdict")
