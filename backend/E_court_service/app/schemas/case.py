from datetime import date
from pydantic import BaseModel


class CourtInfo(BaseModel):
    name: str | None = None
    district: str | None = None
    state: str | None = None
    court_code: int | None = None


class CaseParties(BaseModel):
    petitioners: list[str] = []
    respondents: list[str] = []


class CaseAdvocates(BaseModel):
    petitioner_advocates: list[str] = []
    respondent_advocates: list[str] = []


class CaseHearing(BaseModel):
    next_date: date | None = None
    last_date: date | None = None


class HearingHistoryItem(BaseModel):
    business_on_date: date | None = None
    hearing_date: date | None = None
    purpose: str | None = None
    judge: str | None = None


class CaseOrderItem(BaseModel):
    order_date: date | None = None
    title: str | None = None
    order_type: str | None = None
    file_name: str | None = None
    content_url: str | None = None
    description: str | None = None


class CaseJudges(BaseModel):
    judges: list[str] = []


class CaseResponse(BaseModel):
    cnr: str
    case_number: str | None = None
    case_type: str | None = None
    status: str | None = None

    court: CourtInfo
    parties: CaseParties
    advocates: CaseAdvocates
    judges: CaseJudges
    hearing: CaseHearing
    hearing_history: list[HearingHistoryItem] = []
    orders: list[CaseOrderItem] = []
