from fastapi import APIRouter

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
    return await location_service.get_states()


@router.get(
    "/states/{state_code}/districts",
    response_model=list[DistrictResponse],
)
async def get_districts(state_code: str):
    return await location_service.get_districts(state_code)


@router.get(
    "/states/{state_code}/districts/{district_code}/complexes",
    response_model=list[ComplexResponse],
)
async def get_complexes(
    state_code: str,
    district_code: str,
):
    return await location_service.get_complexes(district_code)


@router.get(
    "/states/{state_code}/districts/{district_code}/complexes/{complex_code}/courts",
    response_model=list[CourtResponse],
)
async def get_courts(
    state_code: str,
    district_code: str,
    complex_code: str,
):
    return await location_service.get_courts(complex_code)
