from pydantic import BaseModel


class StateResponse(BaseModel):
    code: str
    name: str


class DistrictResponse(BaseModel):
    code: str
    name: str


class ComplexResponse(BaseModel):
    code: str
    name: str


class CourtResponse(BaseModel):
    code: str
    name: str
