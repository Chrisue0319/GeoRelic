import math
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_current_admin, get_current_user_or_api_key, rate_limit_read, rate_limit_write
from app.models.poi import POI
from app.models.user import User
from app.schemas.poi import POI as POISchema, POICreate, POIUpdate
from app.utils.exceptions import POIException, ErrorCode

router = APIRouter(prefix="/pois", tags=["POI"])


def _build_query(
    db: Session,
    name: str | None,
    province: str | None,
    poi_type: str | None,
    batch: str | None,
    min_lon: float | None,
    max_lon: float | None,
    min_lat: float | None,
    max_lat: float | None,
    has_image: bool | None,
    has_website: bool | None,
):
    query = db.query(POI)
    if name:
        query = query.filter(POI.name.contains(name))
    if province:
        query = query.filter(POI.address.contains(province))
    if poi_type:
        query = query.filter(POI.type == poi_type)
    if batch:
        query = query.filter(POI.batch == batch)
    if min_lon is not None:
        query = query.filter(POI.lon >= min_lon)
    if max_lon is not None:
        query = query.filter(POI.lon <= max_lon)
    if min_lat is not None:
        query = query.filter(POI.lat >= min_lat)
    if max_lat is not None:
        query = query.filter(POI.lat <= max_lat)
    if has_image is True:
        query = query.filter(POI.image_url.isnot(None))
    if has_image is False:
        query = query.filter(POI.image_url.is_(None))
    if has_website is True:
        query = query.filter(POI.website.isnot(None))
    if has_website is False:
        query = query.filter(POI.website.is_(None))
    return query


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.get("/types/list")
def list_poi_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
    _rate_limit=Depends(rate_limit_read),
):
    types = db.query(POI.type).distinct().all()
    return [t[0] for t in types if t[0]]


@router.get("/batches/list")
def list_poi_batches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
    _rate_limit=Depends(rate_limit_read),
):
    batches = db.query(POI.batch).distinct().all()
    return [b[0] for b in batches if b[0]]


@router.get("/", response_model=list[POISchema])
def list_pois(
    name: str | None = Query(None),
    province: str | None = Query(None),
    poi_type: str | None = Query(None, alias="type"),
    batch: str | None = Query(None),
    min_lon: float | None = Query(None),
    max_lon: float | None = Query(None),
    min_lat: float | None = Query(None),
    max_lat: float | None = Query(None),
    center_lon: float | None = Query(None),
    center_lat: float | None = Query(None),
    radius_km: float | None = Query(None),
    has_image: bool | None = Query(None),
    has_website: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
    _rate_limit=Depends(rate_limit_read),
):
    query = _build_query(db, name, province, poi_type, batch, min_lon, max_lon, min_lat, max_lat, has_image, has_website)
    pois = query.offset(skip).limit(limit).all()
    if center_lat is not None and center_lon is not None and radius_km is not None:
        filtered = []
        for poi in pois:
            if poi.lat is not None and poi.lon is not None:
                d = _haversine_distance(center_lat, center_lon, poi.lat, poi.lon)
                if d <= radius_km:
                    filtered.append(poi)
        return filtered
    return pois


@router.get("/{poi_id}", response_model=POISchema)
def get_poi(
    poi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
    _rate_limit=Depends(rate_limit_read),
):
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise POIException(
            error_code=ErrorCode.POI_NOT_FOUND[0],
            error_desc=ErrorCode.POI_NOT_FOUND[1],
            status_code=status.HTTP_404_NOT_FOUND,
            debug_info=f"POI with id={poi_id} does not exist",
        )
    return poi


@router.post("/", response_model=POISchema, status_code=status.HTTP_201_CREATED)
def create_poi(
    poi_in: POICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    _rate_limit=Depends(rate_limit_write),
):
    poi = POI(**poi_in.model_dump())
    db.add(poi)
    db.commit()
    db.refresh(poi)
    return poi


@router.put("/{poi_id}", response_model=POISchema)
def update_poi(
    poi_id: int,
    poi_in: POIUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    _rate_limit=Depends(rate_limit_write),
):
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise POIException(
            error_code=ErrorCode.POI_NOT_FOUND[0],
            error_desc=ErrorCode.POI_NOT_FOUND[1],
            status_code=status.HTTP_404_NOT_FOUND,
            debug_info=f"POI with id={poi_id} does not exist",
        )
    update_data = poi_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(poi, field, value)
    db.commit()
    db.refresh(poi)
    return poi


@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poi(
    poi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    _rate_limit=Depends(rate_limit_write),
):
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise POIException(
            error_code=ErrorCode.POI_NOT_FOUND[0],
            error_desc=ErrorCode.POI_NOT_FOUND[1],
            status_code=status.HTTP_404_NOT_FOUND,
            debug_info=f"POI with id={poi_id} does not exist",
        )
    db.delete(poi)
    db.commit()
    return None
