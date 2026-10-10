from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CaseOrder(Base):
    __tablename__ = "case_orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_date: Mapped[date | None] = mapped_column(
        Date,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
    )

    order_type: Mapped[str | None] = mapped_column(
        String(100),
    )

    file_name: Mapped[str | None] = mapped_column(
        String(500),
    )

    content_url: Mapped[str | None] = mapped_column(
        String(1000),
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
