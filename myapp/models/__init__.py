from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from .route import Route
from .capacity import Capacity
from .truck_info import TruckInfo
from .order import Order
from .costs import Costs
from .cargo import Cargo
from .margin import Margin
