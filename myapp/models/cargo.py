from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Base  # Import the Base from the main __init__.py

# Define the Cargo table
class Cargo(Base):
    __tablename__ = 'cargo'
    cargo_type = Column(String, primary_key=True)
    cargo_vol = Column(Float)
    cargo_cost = Column(Float)