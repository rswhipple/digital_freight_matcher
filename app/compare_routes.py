from flask import Flask, request, jsonify
from supabase import create_client, Client
import something
from pprint import pprint

app = Flask(__name__)

supabase = create_client(something.url, something.something)
  
  
def process_order(order_id, order_data):
  # create local variables
  order_table = "orders"
  price = 0

  # check if order fits on an existing route
  route_match = compare_routes(order_data)   

  # if route is found, add order to route
  if route_match:
    route = route_match[0]["route_id"]
    order_update = supabase.table(order_table).update({"order_route_id": route}).eq("id", order_id).execute()
    assert len(order_update.data) > 0, "Error: Unable to update orders table with route_id"

  # else create new route
  else: 
    route_match = create_new_route(order_id, order_data)  #*** tony's function, needs to return route_id ***
        
  if is_original(route_match):
    price = calculate_price(order_id)                     #*** tony's function ***
    return price
  
  else:
    results = is_profitable(route_match)                  #*** tony's function, if True returns all orders in route and their prices ***
    if results:
      message = f"New profitable route found, route_id {route_match[0]['route_id']}."
      return message
    else:
      return None
    

def compare_routes(order_data):
  # create local variables
  pick_up = order_data["pick_up"]
  drop_off = order_data["drop_off"]

  # create pickup and dropoff points ON EXISTING ROUTES
  route_match = check_points(pick_up, drop_off)

  if route_match:
    capacity = check_capacity(order_data, route_match)

    if capacity:
      return route_match
    else:
      return None
  else:
    return None
    
  
# pickup and dropoff points come from orders table
def check_points(pickup, drop_off):
  capacity_table = "capacity"

  # Query to check if the point falls on any route
  query = f"""
    SELECT route_id, ST_LineLocatePoint(r.route_geom, {pickup}) AS pickup_loc, 
        ST_LineLocatePoint(r.route_geom, {drop_off}) AS dropoff_loc
    FROM {capacity_table} r
    WHERE ST_DWithin(r.route_geom, {pickup}, 1000)
      AND ST_DWithin(r.route_geom, {drop_off}, 1000)
      AND ST_LineLocatePoint(r.route_geom, {pickup}) <= ST_LineLocatePoint(r.route_geom, {drop_off})
    LIMIT 1;
  """
  
  # Execute the query
  response = supabase.query(query)
  
  if response.status_code == 200:
    route_match = response.get("data")
    return route_match
      
  else:
    print(response.error)


def check_capacity(order_data, route_match):
  route_id = route_match[0]["route_id"]
  pickup = route_match[0]["pickup"]
  drop_off = route_match[0]["drop_off"]
  order_vol = order_data[0]["order_vol"]
  order_weight = order_data[0]["order_weight"]

  capacity_table = "capacity"

  # Query to check if route has capacity
  query = f"""
    SELECT empty_vol > {order_vol} AND empty_weight > {order_weight} AS capacity
    FROM {capacity_table}
    WHERE {route_id} = route_id
      AND ST_Intersects(route_geom, ST_MakeLine({pickup}, {drop_off}))
  """

  # Execute the query
  response = supabase.query(query)

  if response.status_code == 200:
    capacity = response.get("data")
    return capacity
  
  else:
    print(response.error)


# pickup and dropoff points come from orders table
def import_route(points):
  # Mapbox public token
  access_token = "pk.eyJ1IjoicnN3aGlwcGxlIiwiYSI6ImNsb2RlbnN0eTA2bnoyaXQ4aWc1YmF0eGgifQ.nVC4l7HRRRiAYT-A_4ySuA"

  # Convert each point into a string (longitude, latitude) format
  coordinates = ';'.join([f"lon, lat" for lon, lat in points])
  
  # Construct the API request URL
  url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates}?alternatives=true&geometries=geojson&language=en&overview=full&steps=true&access_token={access_token}"

  # Make the API request
  response = requests.get(url)

  # Check if the request was successful 
  if response.status_code == 200:
    # Return route_data as a json object
    route_data = response.json()
    return route_data
  else:
    print("Error: Unable to fetch route data")


def is_in_range(pick_up, drop_off):
  # Set variable for 
  home_base = (-84.3875298776525, 33.754413815792205)

  points = [home_base, pick_up, drop_off, home_base]

  route_data = import_route(points)

  # Check if route is within 10 hours
  if route_data["routes"][0]["duration"] < 36000:
    return True
  else:
    return False
  
def is_original(route_match):
  route_id = route_match[0]["route_id"]
  if route_id >= 1 and route_id <= 5:
    return True
  else:
    return False

# Tony's functions starts here

def add_order_to_route(order_id):
    """adds an order to a given route

    order_id: int -- id of order to add to a route

    return: True if successful, False otherwise
    """
    # get route id
    route_id = supabase.table('orders').select('id', 'order_route_id') \
        .eq('id', order_id).execute()
    route_id = route_id[0]['order_route_id']

    # TODO add pickup and dropoff point to routes table
    # I'm assuming pickup and dropoff are from order and must be put in points
    # format
    
    # TODO update route_geom and capacity in 'capacity' (using Mapbox API)
    # is this same as create_new_route?

    # TODO update confirmed col in orders table 
    # confirm_order()?

    # TODO update margins table

    return True


def create_new_route(order_id, order_data):
    """creates a new route in database

    order_id: int -- order id for needing new route
    order_data: dict -- data of order for new route

    return: id of new route created
    """
    # build new route
    home_base = (-84.3875298776525, 33.754413815792205)
    points = [home_base, order_data["pick_up"], order_data["drop_off"], home_base]
    new_route = {"points": points}

    # insert into 'routes' table
    route_id = supabase.table('routes').insert(new_route).execute()
    route_id = route_id.data[0]["id"]

    # calculate data
    route_data = import_route(points)

    # insert into 'capacity' table
    response = supabase.table('capacity').insert(route_data).execute()

    return route_id


def calculate_price(order_id):
    """calculates the price of a new order

    order_id: int -- order id to use for calculating price

    return: price as float
    """
    # query num of pallets in order
    # TODO where to get num pallets? 2 queries? contract_info + orders?
    #num_pallets = supabase.table('contract_info').select('Routes', 'Pallets') \    
        #.eq('Routes', ?which route?)execute()
    # "pallets" doesn't exist in 'orders' table yet
    num_pallets = supabase.table('orders').select('id', 'pallets') \
        .eq('id', order_id).execute()
    num_pallets = num_pallets.data[0]['pallets']

    # query pallet cost per mile
    pallet_cost_per_mile = supabase.table('costs') \
        .select('pallet_cost_per_mile').execute()
    pallet_cost_per_mile = pallet_cost_per_mile.data[0]['pallets']

    # query markup
    markup = supabase.table('costs').select('markup').execute()
    markup = markup.data[0]['markup']

    return num_pallets * pallet_cost_per_mile * (1 + markup)


def is_profitable(route_id):
    """checks to see if a new route is profitable

    route_id: int -- route id to check

    return: True if profitable, False otherwise
    """
    # query route distance
    total_miles = supabase.table('routes').select('id', 'total_miles') \
        .eq('id', route_id).execute()
    total_miles = total_miles.data[0]['total_miles']

    # query pallet cost per mile
    num_pallets = supabase.table('orders').select('id', 'pallets') \
        .eq('id', order_id).execute()
    num_pallets = num_pallets.data[0]['pallets']

    # query pallet cost per mile
    pallet_cost_per_mile = supabase.table('costs') \
        .select('pallet_cost_per_mile').execute()
    pallet_cost_per_mile = pallet_cost_per_mile.data[0]['pallets']

    # query markup
    markup = supabase.table('costs').select('markup').execute()
    markup = markup.data[0]['markup']

    OTC = total_miles * calc_total_costs()
    cargo_cost = num_pallets * pallet_cost_per_mile
    new_price = cargo_cost * (1 + markup)
    margin = (new_price - OTC) / OTC

    return margin > 0


def calc_total_costs():
    """Calculate total costs from spreadsheet

    Total = Trucker + Fuel + Leasing + Maintenance + Insurance

    return: total cost
    note: 'costs' table setup wrong direction
    """
    trucker = supabase.table('costs').select('trucker_cost').execute()
    trucker = trucker.data[0]['trucker']

    fuel = supabase.table('costs').select('fuel_cost').execute()
    fuel = fuel.data[0]['fuel']

    leasing = supabase.table('costs').select('leasing_cost').execute()
    leasing = leasing.data[0]['leasing']

    maintenance = supabase.table('costs').select('maintenance_cost').execute()
    maintenance = maintenance.data[0]['maintenance']

    insurance = supabase.table('costs').select('insurance_cost').execute()
    insurance = insurance.data[0]['insurance']

    return trucker + fuel + leasing + maintenance + insurance