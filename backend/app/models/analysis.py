import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Analysis(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analyses"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    input_type: Mapped[str] = mapped_column(Text, nullable=False)  # text | url | pdf
    input_raw: Mapped[Optional[str]] = mapped_column(Text)
    policy_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, default="pending"
    )  # pending | processing | complete | failed
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_msg: Mapped[Optional[str]] = mapped_column(Text)

    verdict = relationship("Verdict", back_populates="analysis", uselist=False)
    sources = relationship("Source", back_populates="analysis")
