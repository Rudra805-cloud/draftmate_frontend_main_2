from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.search import (
    CaseSearchRequest,
    CaseSearchResponse,
)
from app.services.case_search_service import CaseSearchService


router = APIRouter(prefix="/cases", tags=["Case Search"])

search_service = CaseSearchService()


@router.post("/search", response_model=CaseSearchResponse)
async def search_cases(
    request: CaseSearchRequest,
    db: Session = Depends(get_db),
):
    items, total = await search_service.search_cases(
        db=db,
        query=request.query,
        state_code=request.state_code,
        district_code=request.district_code,
        court_code=request.court_code,
        case_type=request.case_type,
        case_status=request.case_status,
        filing_year=request.filing_year,
        filing_date_from=request.filing_date_from,
        filing_date_to=request.filing_date_to,
        page=request.page,
        limit=request.limit,
    )

    return CaseSearchResponse(
        items=items,
        page=request.page,
        limit=request.limit,
        total=total,
    )
