"""Initial MVP schema.

Revision ID: 0001_initial_mvp
Revises:
Create Date: 2026-08-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_mvp"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=40), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("primary_goal", sa.String(length=120), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False),
        sa.Column("consent_version", sa.String(length=40), nullable=True),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"], unique=True)

    op.create_table(
        "assessment_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instrument_code", sa.String(length=80), nullable=False),
        sa.Column("instrument_version", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("raw_score", sa.Integer(), nullable=True),
        sa.Column("normalized_score", sa.Integer(), nullable=True),
        sa.Column("classification", sa.String(length=80), nullable=True),
        sa.Column("result_payload", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assessment_sessions_instrument_code", "assessment_sessions", ["instrument_code"], unique=False)
    op.create_index("ix_assessment_sessions_status", "assessment_sessions", ["status"], unique=False)
    op.create_index("ix_assessment_sessions_user_id", "assessment_sessions", ["user_id"], unique=False)

    op.create_table(
        "assessment_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_code", sa.String(length=80), nullable=False),
        sa.Column("numeric_value", sa.Integer(), nullable=True),
        sa.Column("text_value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["assessment_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assessment_responses_session_id", "assessment_responses", ["session_id"], unique=False)

    op.create_table(
        "daily_checkins",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("checkin_date", sa.Date(), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=False),
        sa.Column("anxiety", sa.Integer(), nullable=False),
        sa.Column("energy", sa.Integer(), nullable=False),
        sa.Column("stress", sa.Integer(), nullable=False),
        sa.Column("sleep_quality", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "checkin_date", name="uq_daily_checkin_user_date"),
    )
    op.create_index("ix_daily_checkins_checkin_date", "daily_checkins", ["checkin_date"], unique=False)
    op.create_index("ix_daily_checkins_user_id", "daily_checkins", ["user_id"], unique=False)

    op.create_table(
        "journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("mood_label", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_journal_entries_created_at", "journal_entries", ["created_at"], unique=False)
    op.create_index("ix_journal_entries_user_id", "journal_entries", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_journal_entries_user_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_created_at", table_name="journal_entries")
    op.drop_table("journal_entries")
    op.drop_index("ix_daily_checkins_user_id", table_name="daily_checkins")
    op.drop_index("ix_daily_checkins_checkin_date", table_name="daily_checkins")
    op.drop_table("daily_checkins")
    op.drop_index("ix_assessment_responses_session_id", table_name="assessment_responses")
    op.drop_table("assessment_responses")
    op.drop_index("ix_assessment_sessions_user_id", table_name="assessment_sessions")
    op.drop_index("ix_assessment_sessions_status", table_name="assessment_sessions")
    op.drop_index("ix_assessment_sessions_instrument_code", table_name="assessment_sessions")
    op.drop_table("assessment_sessions")
    op.drop_index("ix_profiles_user_id", table_name="profiles")
    op.drop_table("profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
