from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY data type

Base = declarative_base()
class Capacity(Base):
    __tablename__ = 'capacity'
    route_id = Column(Integer, ForeignKey('routes.route_id'), primary_key=True)
    # to store latitude and longitude coordinates as an array
    route_geom = Column(ARRAY(Float))
    empty_vol = Column(Float, default=1700)
    empty_weight = Column(Float, default=9180)
