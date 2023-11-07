from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY data type

Base = declarative_base()

# Define the TruckInfo table
class TruckInfo(Base):
    __tablename__ = 'truck_info'
    truck_id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.route_id'))
    # to store latitude and longitude coordinates as an array
    route_geom = Column(ARRAY(Float))
    capacity_vol = Column(Float, default=1700)
    capacity_weight = Column(Float, default=9180)
    # Calculate this
    pallet_cost = Column(Float)
    std_package_cost = Column(Float)