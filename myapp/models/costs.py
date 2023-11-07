from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Base  # Import the Base from the main __init__.py

# Define the Costs table
class Costs(Base):
    __tablename__ = 'costs'
    total_cost = Column(Float, primary_key=True)
    trucker = Column(Float)
    fuel = Column(Float)
    leasing = Column(Float)
    maintenance = Column(Float)
    insurance = Column(Float)
    miles_gallon = Column(Float)
    gas_price = Column(Float)