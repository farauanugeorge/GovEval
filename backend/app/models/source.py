import uuid
from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Source(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sources"

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False
    )
    doi: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[Optional[str]] = mapped_column(Text)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    origin: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # semantic_scholar | openalex | pubmed
    relevance_score: Mapped[Optional[float]] = mapped_column(Float)
    used_in_verdict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    analysis = relationship("Analysis", back_populates="sources")
    embedding = relationship("Embedding", back_populates="source", uselist=False)
