from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY data type

Base = declarative_base()

class Route(Base):
    __tablename__ = 'routes'
    route_id = Column(Integer, primary_key=True)
    total_miles = Column(Float)
    total_time = Column(Float)
    # points column to store latitude and longitude coordinates as an array
    points = Column(ARRAY(Float))  # to store coordinates as an array of floats

