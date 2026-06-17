from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class LandmarkResponse(BaseModel):
    uuid: str
    name: str
    emoji: str
    description: str
    fact: str
    year: str
    public_key: str = ""
