from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CaseHearing(Base):
    __tablename__ = "case_hearings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    business_on_date: Mapped[date | None] = mapped_column(
        Date,
    )

    hearing_date: Mapped[date | None] = mapped_column(
        Date,
        index=True,
    )

    purpose: Mapped[str | None] = mapped_column(
        String(255),
    )

    judge: Mapped[str | None] = mapped_column(
        String(255),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
