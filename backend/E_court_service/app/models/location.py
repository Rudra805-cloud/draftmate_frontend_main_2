from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    state_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    state_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    district_code: Mapped[str | None] = mapped_column(
        String(20),
        index=True,
    )

    district_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    complex_code: Mapped[str | None] = mapped_column(
        String(20),
        index=True,
    )

    complex_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    court_code: Mapped[str | None] = mapped_column(
        String(30),
        index=True,
    )

    court_name: Mapped[str | None] = mapped_column(
        String(255),
    )
