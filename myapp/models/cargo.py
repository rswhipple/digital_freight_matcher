from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY data type

Base = declarative_base()

# Define the Cargo table
class Cargo(Base):
    __tablename__ = 'cargo'
    cargo_type = Column(String, primary_key=True)
    cargo_vol = Column(Float)
    cargo_cost = Column(Float)