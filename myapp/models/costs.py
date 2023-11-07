from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY data type

Base = declarative_base()

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