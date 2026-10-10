"""store auth user ids as text

Revision ID: 4f2a7b9c1d10
Revises: 3ee586d22216
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4f2a7b9c1d10"
down_revision: Union[str, None] = "3ee586d22216"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tracked_cases",
        "user_id",
        existing_type=sa.Integer(),
        type_=sa.String(length=64),
        existing_nullable=False,
        postgresql_using="user_id::text",
    )


def downgrade() -> None:
    op.alter_column(
        "tracked_cases",
        "user_id",
        existing_type=sa.String(length=64),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="user_id::integer",
    )
