"""add case judges

Revision ID: 306883d715be
Revises: ff9606939d9f
Create Date: 2026-10-09 00:57:15.239314

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "306883d715be"
down_revision: Union[str, None] = "ff9606939d9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "case_judges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_case_judges_case_id",
        "case_judges",
        ["case_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_case_judges_case_id",
        table_name="case_judges",
    )

    op.drop_table("case_judges")
