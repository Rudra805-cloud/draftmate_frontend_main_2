import httpx

from app.core.config import settings
from app.core.exceptions import (
    CaseNotFoundError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from app.providers.base import CourtProvider


class ECourtsProvider(CourtProvider):
    def __init__(self):
        self.base_url = settings.ecourts_base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {settings.ecourts_api_key}"}

    async def search_cases(self, **filters):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/partner/search",
                headers=self.headers,
                params=filters,
            )

        self._handle_response(response)

        return response.json()

    async def get_case(self, cnr: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/partner/case/{cnr}",
                headers=self.headers,
            )

        self._handle_response(response)

        return response.json()

    async def refresh_case(self, cnr: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/partner/case/{cnr}/refresh",
                headers=self.headers,
            )

        self._handle_response(response)

        return response.json()

    async def get_states(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/partner/causelist/court-structure/states",
                headers=self.headers,
            )

        self._handle_response(response)

        return response.json()

    async def get_districts(self, state_code: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/partner/causelist/court-structure/states/{state_code}/districts",
                headers=self.headers,
            )

        self._handle_response(response)
        return response.json()

    async def get_complexes(self, state_code: str, district_code: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/partner/causelist/court-structure/states/{state_code}/districts/{district_code}/complexes",
                headers=self.headers,
            )

        self._handle_response(response)

        return response.json()

    async def get_courts(
        self,
        state_code: str,
        district_code: str,
        complex_code: str,
    ):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/partner/causelist/court-structure/states/{state_code}/districts/{district_code}/complexes/{complex_code}/courts",
                headers=self.headers,
            )

        self._handle_response(response)

        return response.json()

    @staticmethod
    def _handle_response(response: httpx.Response) -> None:
        if response.status_code == 404:
            raise CaseNotFoundError()

        if response.status_code in (401, 403):
            raise ProviderAuthenticationError()

        if response.status_code == 429:
            raise ProviderRateLimitError()

        if response.status_code >= 500:
            raise ProviderUnavailableError()

        response.raise_for_status()
