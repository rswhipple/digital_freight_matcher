from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY  # Import ARRAY data type
from . import Base  # Import the Base from the main __init__.py


# Define the Orders table
class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.route_id'))
    # to store coordinates as an array of floats
    pickup = Column(ARRAY(Float))
    drop_off = Column(ARRAY(Float))
    cargo_type = Column(String)
    total_vol = Column(Float)
    total_weight = Column(Float)
    price = Column(Float)  # Calculate this
    confirmed = Column(Boolean, default=False)
