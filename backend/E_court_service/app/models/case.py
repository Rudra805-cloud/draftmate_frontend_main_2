from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    cnr: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
        nullable=False,
    )

    case_number: Mapped[str | None] = mapped_column(String(100))

    case_type: Mapped[str | None] = mapped_column(String(100))

    status: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(10),
        index=True,
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
    )

    court_name: Mapped[str | None] = mapped_column(String(255))

    filing_date: Mapped[date | None] = mapped_column(Date)

    registration_date: Mapped[date | None] = mapped_column(Date)

    first_hearing_date: Mapped[date | None] = mapped_column(Date)

    next_hearing_date: Mapped[date | None] = mapped_column(
        Date,
        index=True,
    )

    last_hearing_date: Mapped[date | None] = mapped_column(Date)

    decision_date: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
