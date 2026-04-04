import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.config import settings


class Embedding(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "embeddings"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False
    )
    embedding = mapped_column(Vector(settings.embedding_dim))

    source = relationship("Source", back_populates="embedding")
