from fastapi import APIRouter, HTTPException

from app.core.exceptions import (
    CaseNotFoundError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from app.schemas.location import (
    StateResponse,
    DistrictResponse,
    ComplexResponse,
    CourtResponse,
)
from app.services.location_service import LocationService


router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
)

location_service = LocationService()


@router.get("/states", response_model=list[StateResponse])
async def get_states():
    return await _get_location_data(location_service.get_states)


@router.get(
    "/states/{state_code}/districts",
    response_model=list[DistrictResponse],
)
async def get_districts(state_code: str):
    return await _get_location_data(location_service.get_districts, state_code)


@router.get(
    "/states/{state_code}/districts/{district_code}/complexes",
    response_model=list[ComplexResponse],
)
async def get_complexes(
    state_code: str,
    district_code: str,
):
    return await _get_location_data(
        location_service.get_complexes,
        state_code,
        district_code,
    )


@router.get(
    "/states/{state_code}/districts/{district_code}/complexes/{complex_code}/courts",
    response_model=list[CourtResponse],
)
async def get_courts(
    state_code: str,
    district_code: str,
    complex_code: str,
):
    return await _get_location_data(
        location_service.get_courts,
        state_code,
        district_code,
        complex_code,
    )


async def _get_location_data(operation, *args):
    try:
        return await operation(*args)
    except CaseNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Location not found",
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
