from datetime import date

from pydantic import BaseModel, Field


class CaseSearchRequest(BaseModel):
    query: str | None = Field(default=None, min_length=1)

    state_code: str | None = None
    district_code: str | None = None
    court_code: str | None = None

    case_type: str | None = None
    case_status: str | None = None
    filing_year: int | None = Field(default=None, ge=1950, le=2100)

    filing_date_from: date | None = None
    filing_date_to: date | None = None

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class CaseSearchItem(BaseModel):
    cnr: str
    case_number: str | None = None
    case_type: str | None = None
    status: str | None = None

    court_code: str | None = None

    judges: list[str] = Field(default_factory=list)
    petitioners: list[str] = Field(default_factory=list)
    respondents: list[str] = Field(default_factory=list)
    advocates: list[str] = Field(default_factory=list)

    filing_date: date | None = None
    registration_date: date | None = None
    decision_date: date | None = None
    next_hearing_date: date | None = None

    case_category: str | None = None
    judicial_section: str | None = None


class CaseSearchResponse(BaseModel):
    items: list[CaseSearchItem]
    page: int
    limit: int
    total: int | None = None
