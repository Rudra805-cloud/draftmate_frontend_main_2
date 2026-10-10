from sqlalchemy.orm import Session

from app.providers.ecourts import ECourtsProvider
from app.schemas.search import CaseSearchItem


class CaseSearchService:
    def __init__(self):
        self.provider = ECourtsProvider()

    async def search_cases(
        self,
        db: Session,
        query: str | None = None,
        state_code: str | None = None,
        district_code: str | None = None,
        court_code: str | None = None,
        case_type: str | None = None,
        case_status: str | None = None,
        filing_year: int | None = None,
        filing_date_from=None,
        filing_date_to=None,
        page: int = 1,
        limit: int = 20,
    ):
        # Search results are NOT stored in DB.
        # Always search eCourts directly.

        filters = {
            "page": page,
            "pageSize": limit,
        }

        if query:
            filters["query"] = query

        if state_code:
            filters["stateCode"] = state_code

        if district_code:
            filters["districtCode"] = district_code

        if court_code:
            filters["courtCodes"] = court_code

        if case_type:
            filters["caseType"] = case_type

        if case_status:
            filters["caseStatus"] = case_status

        if filing_year:
            filters["filingYear"] = filing_year

        if filing_date_from:
            filters["filingDateFrom"] = filing_date_from.isoformat()

        if filing_date_to:
            filters["filingDateTo"] = filing_date_to.isoformat()

        # Call eCourts Search API
        provider_response = await self.provider.search_cases(**filters)

        # eCourts response:
        #
        # {
        #     "data": {
        #         "results": [...],
        #         "totalHits": 150,
        #         ...
        #     }
        # }

        data = provider_response.get("data", {})

        provider_items = data.get("results", [])

        search_items = [
            CaseSearchItem(
                cnr=item.get("cnr"),
                case_number=item.get("registrationNumber"),
                case_type=item.get("caseType"),
                status=item.get("caseStatus"),
                court_code=item.get("courtCode"),
                judges=item.get("judges", []),
                petitioners=item.get("petitioners", []),
                respondents=item.get("respondents", []),
                advocates=item.get("petitionerAdvocates", []),
                filing_date=item.get("filingDate"),
                registration_date=item.get("registrationDate"),
                decision_date=item.get("decisionDate"),
                next_hearing_date=item.get("nextHearingDate"),
                case_category=item.get("caseCategory"),
                judicial_section=item.get("judicialSection"),
            )
            for item in provider_items
            if item.get("cnr")
        ]

        # eCourts uses totalHits
        provider_total = data.get("totalHits", 0)

        return search_items, provider_total
