from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY data type

Base = declarative_base()

# Define the Margins table
class Margin(Base):
    __tablename__ = 'margins'
    route_id = Column(Integer, ForeignKey('routes.route_id'), primary_key=True)
    # needs Calculation
    operational_cost = Column(Float)
    income = Column(Float)
    margin = Column(Float)