from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import get_db, get_current_user_id
from app.models.case import Case
from app.models.tracked_case import TrackedCase
from app.services.case_service import CaseService
from app.core.exceptions import (
    CaseNotFoundError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)

router = APIRouter(prefix="/tracking", tags=["Case Tracking"])
case_service = CaseService()


def _provider_error(error: Exception) -> HTTPException:
    if isinstance(error, ProviderAuthenticationError):
        return HTTPException(
            status_code=502,
            detail="Court provider authentication failed",
        )
    if isinstance(error, ProviderRateLimitError):
        return HTTPException(
            status_code=429,
            detail="Court provider rate limit exceeded",
        )
    if isinstance(error, ProviderUnavailableError):
        return HTTPException(
            status_code=503,
            detail="Court provider temporarily unavailable",
        )
    return HTTPException(status_code=500, detail="Unable to load case")


def _tracking_response(tracked: TrackedCase, case: Case) -> dict:
    return {
        "tracking_id": tracked.id,
        "cnr": case.cnr,
        "case_id": case.id,
        "is_active": tracked.is_active,
        "status": case.status,
        "case_number": case.case_number,
        "case_type": case.case_type,
        "state": case.state,
        "district": case.district,
        "court_name": case.court_name,
        "next_hearing_date": case.next_hearing_date,
        "updated_at": tracked.updated_at,
    }


@router.get("")
def list_tracked_cases(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Return all active cases tracked by the authenticated user."""
    tracked_cases = (
        db.query(TrackedCase, Case)
        .join(Case, Case.id == TrackedCase.case_id)
        .filter(
            TrackedCase.user_id == user_id,
            TrackedCase.is_active.is_(True),
        )
        .order_by(TrackedCase.updated_at.desc())
        .all()
    )
    return [_tracking_response(tracked, case) for tracked, case in tracked_cases]


@router.post("/{cnr}/refresh")
async def refresh_tracked_case(
    cnr: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Fetch the latest provider data for an already tracked case."""
    tracked_case = (
        db.query(TrackedCase)
        .join(Case, Case.id == TrackedCase.case_id)
        .filter(
            TrackedCase.user_id == user_id,
            TrackedCase.is_active.is_(True),
            Case.cnr == cnr,
        )
        .first()
    )
    if not tracked_case:
        raise HTTPException(status_code=404, detail="Tracked case not found")

    try:
        await case_service.get_case(db, cnr)
    except CaseNotFoundError:
        raise HTTPException(status_code=404, detail="Case not found")
    except (
        ProviderAuthenticationError,
        ProviderRateLimitError,
        ProviderUnavailableError,
    ) as error:
        raise _provider_error(error) from error

    case = db.query(Case).filter(Case.cnr == cnr).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return _tracking_response(tracked_case, case)


@router.post("/{cnr}")
async def track_case(
    cnr: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        await case_service.get_case(db, cnr)
    except CaseNotFoundError:
        raise HTTPException(status_code=404, detail="Case not found")
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

    case = db.query(Case).filter(Case.cnr == cnr).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    tracked = (
        db.query(TrackedCase)
        .filter(
            TrackedCase.user_id == user_id,
            TrackedCase.case_id == case.id,
        )
        .first()
    )

    if tracked:
        if tracked.is_active:
            return {
                "message": "Case is already tracked",
                "cnr": case.cnr,
                "is_active": True,
            }

        tracked.is_active = True
    else:
        tracked = TrackedCase(
            user_id=user_id,
            case_id=case.id,
            is_active=True,
        )
        db.add(tracked)

    try:
        db.commit()
        db.refresh(tracked)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to track case",
        ) from error

    return {
        "message": "Case tracked successfully",
        "cnr": case.cnr,
        "is_active": tracked.is_active,
    }


@router.delete("/{cnr}")
def untrack_case(
    cnr: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    case = db.query(Case).filter(Case.cnr == cnr).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    tracked = (
        db.query(TrackedCase)
        .filter(
            TrackedCase.user_id == user_id,
            TrackedCase.case_id == case.id,
        )
        .first()
    )

    if not tracked or not tracked.is_active:
        raise HTTPException(
            status_code=404,
            detail="Tracked case not found",
        )

    tracked.is_active = False

    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to untrack case",
        ) from error

    return {
        "message": "Case untracked successfully",
        "cnr": case.cnr,
        "is_active": False,
    }
