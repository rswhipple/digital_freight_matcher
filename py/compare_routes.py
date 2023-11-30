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
