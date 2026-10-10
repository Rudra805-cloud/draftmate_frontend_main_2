from datetime import date

from app.models.case import Case


def parse_date(value) -> date | None:
    if not value:
        return None

    if isinstance(value, date):
        return value

    return date.fromisoformat(value)


def map_provider_case(data: dict) -> Case:
    return Case(
        cnr=data["cnr"],
        case_number=(
            data.get("registrationNumber") or data.get("filingNumber") or None
        ),
        case_type=data.get("caseType"),
        status=data.get("caseStatus"),
        state=data.get("stateCode"),
        district=data.get("districtCode"),
        court_name=None,
        filing_date=parse_date(data.get("filingDate")),
        registration_date=parse_date(data.get("registrationDate")),
        first_hearing_date=parse_date(data.get("firstHearingDate")),
        next_hearing_date=parse_date(data.get("nextHearingDate")),
        last_hearing_date=parse_date(data.get("lastHearingDate")),
        decision_date=parse_date(data.get("decisionDate")),
    )
