from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from geoalchemy2 import Geometry
from app.database import Base


class POI(Base):
    __tablename__ = "pois"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, index=True)
    class_code = Column(String(50), index=True)
    name = Column(String(200), index=True, nullable=False)
    age = Column(String(200))
    address = Column(String(300))
    type = Column(String(50), index=True)
    batch = Column(String(20), index=True)
    remark = Column(Text)
    bd_lon = Column(Float)
    bd_lat = Column(Float)
    lon = Column(Float, index=True)
    lat = Column(Float, index=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=True)
    image_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
