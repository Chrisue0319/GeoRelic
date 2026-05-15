from datetime import datetime
from pydantic import BaseModel, Field


class POIBase(BaseModel):
    code: int | None = None
    class_code: str | None = None
    name: str
    age: str | None = None
    address: str | None = None
    type: str | None = None
    batch: str | None = None
    remark: str | None = None
    bd_lon: float | None = None
    bd_lat: float | None = None
    lon: float | None = None
    lat: float | None = None
    image_url: str | None = None
    website: str | None = None


class POICreate(POIBase):
    pass


class POIUpdate(BaseModel):
    code: int | None = None
    class_code: str | None = None
    name: str | None = None
    age: str | None = None
    address: str | None = None
    type: str | None = None
    batch: str | None = None
    remark: str | None = None
    bd_lon: float | None = None
    bd_lat: float | None = None
    lon: float | None = None
    lat: float | None = None
    image_url: str | None = None
    website: str | None = None


class POI(POIBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class POIQuery(BaseModel):
    name: str | None = None
    province: str | None = None
    type: str | None = None
    batch: str | None = None
    min_lon: float | None = None
    max_lon: float | None = None
    min_lat: float | None = None
    max_lat: float | None = None
    center_lon: float | None = None
    center_lat: float | None = None
    radius_km: float | None = None
    has_image: bool | None = None
    has_website: bool | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
