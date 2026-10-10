from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    CaseNotFoundError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from app.schemas.case import CaseResponse
from app.services.case_service import CaseService


router = APIRouter(prefix="/cases", tags=["Cases"])

case_service = CaseService()


@router.get("/{cnr}", response_model=CaseResponse)
async def get_case(
    cnr: str,
    db: Session = Depends(get_db),
):
    try:
        return await case_service.get_case(db, cnr)

    except CaseNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    except ProviderAuthenticationError:
        raise HTTPException(
            status_code=502,
            detail="Court provider authentication failed",
        )

    except ProviderRateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Court provider rate limit exceeded",
        )

    except ProviderUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Court provider temporarily unavailable",
        )
