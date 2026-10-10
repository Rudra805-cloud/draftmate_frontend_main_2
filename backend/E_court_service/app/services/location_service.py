from app.providers.ecourts import ECourtsProvider
from app.schemas.location import (
    StateResponse,
    DistrictResponse,
    ComplexResponse,
    CourtResponse,
)


class LocationService:
    def __init__(self):
        self.provider = ECourtsProvider()

    async def get_states(self):
        provider_response = await self.provider.get_states()

        return [
            StateResponse(
                code=item.get("state"),
                name=item.get("stateName"),
            )
            for item in provider_response
        ]

    async def get_districts(self, state_code: str):
        provider_response = await self.provider.get_districts(state_code)

        return [
            DistrictResponse(
                code=item.get("districtCode"),
                name=item.get("districtName"),
            )
            for item in provider_response
        ]

    async def get_complexes(self, district_code: str):
        provider_response = await self.provider.get_complexes(district_code)

        return [
            ComplexResponse(
                code=item.get("complexCode"),
                name=item.get("complexName"),
            )
            for item in provider_response
        ]

    async def get_courts(self, complex_code: str):
        provider_response = await self.provider.get_courts(complex_code)

        return [
            CourtResponse(
                code=item.get("courtCode"),
                name=item.get("courtName"),
            )
            for item in provider_response
        ]
