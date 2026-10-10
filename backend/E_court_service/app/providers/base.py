from abc import ABC, abstractmethod


class CourtProvider(ABC):
    @abstractmethod
    async def search_cases(self, **filters):
        pass

    @abstractmethod
    async def get_case(self, cnr: str):
        pass

    @abstractmethod
    async def refresh_case(self, cnr: str):
        pass

    @abstractmethod
    async def get_states(self):
        pass

    @abstractmethod
    async def get_districts(self, state_code: str):
        pass

    @abstractmethod
    async def get_complexes(self, state_code: str, district_code: str):
        pass

    @abstractmethod
    async def get_courts(
        self,
        state_code: str,
        district_code: str,
        complex_code: str,
    ):
        pass
