from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.case import Case


class CaseRepository:
    @staticmethod
    def get_by_cnr(db: Session, cnr: str) -> Case | None:
        stmt = select(Case).where(Case.cnr == cnr)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_id(db: Session, case_id: int) -> Case | None:
        stmt = select(Case).where(Case.id == case_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, case: Case) -> Case:
        db.add(case)
        db.commit()
        db.refresh(case)

        return case

    @staticmethod
    def update(db: Session, case: Case) -> Case:
        db.commit()
        db.refresh(case)

        return case
