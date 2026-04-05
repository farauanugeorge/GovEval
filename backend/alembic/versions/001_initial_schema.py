"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "analyses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("input_type", sa.Text(), nullable=False),
        sa.Column("input_raw", sa.Text()),
        sa.Column("policy_text", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_msg", sa.Text()),
    )

    op.create_table(
        "verdicts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("analysis_id", UUID(as_uuid=True), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("verdict", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("studies_used", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("evidence_for", JSONB(), nullable=False, server_default="[]"),
        sa.Column("evidence_against", JSONB(), nullable=False, server_default="[]"),
        sa.Column("raw_llm_output", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_confidence_range"),
    )

    op.create_table(
        "sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("analysis_id", UUID(as_uuid=True), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("doi", sa.Text()),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authors", sa.Text()),
        sa.Column("year", sa.Integer()),
        sa.Column("abstract", sa.Text(), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("relevance_score", sa.Float()),
        sa.Column("used_in_verdict", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "embeddings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    # Add vector column (alembic doesn't support pgvector natively)
    op.execute("ALTER TABLE embeddings ADD COLUMN embedding vector(384)")
    op.execute("CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)")


def downgrade() -> None:
    op.drop_table("embeddings")
    op.drop_table("sources")
    op.drop_table("verdicts")
    op.drop_table("analyses")
