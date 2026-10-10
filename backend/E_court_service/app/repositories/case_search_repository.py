from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.case import Case


class CaseSearchRepository:
    @staticmethod
    def search(
        db: Session,
        query: str | None = None,
        state_code: str | None = None,
        district_code: str | None = None,
        court_code: int | None = None,
        case_type: str | None = None,
        case_status: str | None = None,
        filing_year: int | None = None,
        filing_date_from=None,
        filing_date_to=None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Case], int]:

        stmt = select(Case)
        count_stmt = select(func.count()).select_from(Case)

        conditions = []

        if query:
            search = f"%{query.strip()}%"

            conditions.append(
                or_(
                    Case.cnr.ilike(search),
                    Case.case_number.ilike(search),
                    Case.case_type.ilike(search),
                    Case.court_name.ilike(search),
                )
            )

        if state_code:
            conditions.append(Case.state == state_code)

        if district_code:
            conditions.append(Case.district == district_code)

        if court_code:
            # Current Case model stores court_name, not court_code.
            # Court-code filtering will be added after location normalization.
            pass

        if case_type:
            conditions.append(Case.case_type == case_type)

        if case_status:
            conditions.append(Case.status == case_status)

        if filing_year:
            conditions.append(func.extract("year", Case.filing_date) == filing_year)

        if filing_date_from:
            conditions.append(Case.filing_date >= filing_date_from)

        if filing_date_to:
            conditions.append(Case.filing_date <= filing_date_to)

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        offset = (page - 1) * limit

        stmt = stmt.order_by(Case.updated_at.desc()).offset(offset).limit(limit)

        cases = list(db.execute(stmt).scalars().all())
        total = db.execute(count_stmt).scalar_one()

        return cases, total
