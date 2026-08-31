from pydantic import BaseModel


class AreaConfigModel(BaseModel):
    name: str
    enabled: bool


class ZoneConfigModel(BaseModel):
    name: str
    enabled: bool


class FlowConfigModel(BaseModel):
    host: str
    port: int
    serial_number: str
    username: str | None = None
    password: str | None = None
    areas: dict[int, AreaConfigModel]
    zones: dict[int, ZoneConfigModel]