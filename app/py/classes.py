class Route:
  def __init__(self, route_id, points, total_miles, total_time):
    self.route_id = route_id
    self.points = points
    self.total_miles = total_miles
    self.total_time = total_time

  def __str__(self):
    return f"route_id: {self.route_id}, points: {self.points}, total_miles: {self.total_miles}, total_time: {self.total_time}"

class Capacity:
  def __init__(self, route_id, route_geom, empty_vol, empty_weight):
    self.route_id = route_id
    self.route_geom = route_geom
    self.empty_vol = 1700
    self.empty_weight = 9180

  def __str__(self):
    return f"route_id: {self.route_id}, route_geom: {self.route_geom}, empty_vol: {self.empty_vol}, empty_weight: {self.empty_weight}"
  
class TruckInfo:
  def __init__(self, route_id, capacity_vol, capacity_weight):
    self.route_id = route_id
    self.capacity_vol = 1700
    self.capacity_weight = 9180

  def __str__(self):
    return f"truck_id: {self.truck_id}, capacity_vol: {self.capacity_vol}, capacity_weight: {self.capacity_weight}"

class Order:
  def __init__(self, order_id, pickup, drop_off, cargo, price, confirmed):
    self.order_id = order_id
    self.pickup = pickup
    self.drop_off = drop_off
    self.cargo = cargo
    self.price = None
    self.confirmed = False

  def __str__(self):
    return f"order_id: {self.order_id}, pickup: {self.pickup}, drop_off: {self.drop_off}, cargo: {self.cargo}, price: {self.price}, confirmed: {self.confirmed}"
  
class Cost:
  def __init__(self, total_cost, trucker, fuel, leasing, maintenance, insurance, miles_gallon, gas_price):
    self.total_cost = trucker + fuel + leasing + maintenance + insurance
    self.trucker = trucker
    self.fuel = gas_price / miles_gallon
    self.leasing = leasing
    self.maintenance = maintenance
    self.insurance = insurance
    self.miles_gallon = miles_gallon
    self.gas_price = gas_price

  def __str__(self):
    return f"total_cost: {self.total_cost}, trucker: {self.trucker}, fuel: {self.fuel}, leasing: {self.leasing}, maintenance: {self.maintenance}, insurance: {self.insurance}, miles_gallon: {self.miles_gallon}, gas_price: {self.gas_price}"
  
class Cargo:
  def __init__(self, cargo_type, cargo_vol, cargo_cost):
    self.cargo_type = cargo_type
    self.cargo_vol = cargo_vol
    self.cargo_cost = cargo_cost

  def __str__(self):
    return f"cargo_type: {self.cargo_type}, cargo_vol: {self.cargo_vol}, cargo_cost: {self.cargo_cost}"
  
class Margin:
  def __init__(self, route_id, operational_cost, income, margin):
    self.route_id = route_id
    self.operational_cost = operational_cost
    self.income = income
    self.margin = margin