from flask import Flask, json
from supabase import create_client, Client
import something
from pprint import pprint
import requests

METERS2MILES = 0.000621371

app = Flask(__name__)

supabase = create_client(something.url, something.something)
  
  
def process_order(order_data, order_id):
  # create local variables
  order_table = "orders"
  price = 0
  route_id = 0

  # check if order fits on an existing route
  route_match = compare_routes(order_data)   

  # if route is found, add order to route
  if route_match:
    # add route_id to order
    route_id = route_match[0]["route_id"]
    order_update = supabase.table(order_table).update({"order_route_id": route_id}).eq("id", order_id).execute()
    assert len(order_update.data) > 0, "Error: Unable to update orders table with route_id"
    # add order to route
    add_order_to_route(route_match, order_data, order_id)

  # if there is no match, create a new route
  else: 
    route_id = create_new_route(order_id)
        
  if route_match:
    price = calculate_price(order_id, order_data, route_id)
    return price
  
  else:
    results = is_profitable(route_match)  #if True returns all orders in route and their prices *** RWS
    if results:
      message = f"New profitable route found, route_id {route_match[0]['route_id']}."
      return message
    else:
      return None
    

def compare_routes(order_data):
  # create local variables
  pickup = order_data["pick_up"]
  dropoff = order_data["drop_off"]

  # create pickup and dropoff points ON EXISTING ROUTES
  route_match = check_points(pickup, dropoff)

  if route_match:
    capacity = check_capacity(order_data, route_match)

    if capacity:
      return route_match
    else:
      return None
  else:
    return None
    
  
# pickup and dropoff points come from orders table
def check_points(pickup, dropoff):
  # create local variables
  routes_table = "routes"

  # Query to check if the point falls on any route
  query = f"""
    SELECT r.route_id, ST_LineLocatePoint(r.route_geom, {pickup}) AS closest_point_to_p, 
        ST_LineLocatePoint(r.route_geom, {dropoff}) AS closest_point_to_d
    FROM {routes_table} r
    WHERE ST_DWithin(r.route_geom, {pickup}, 1000)
      AND ST_DWithin(r.route_geom, {dropoff}, 1000)
      AND ST_LineLocatePoint(r.route_geom, {pickup}) <= ST_LineLocatePoint(r.route_geom, {dropoff})
    LIMIT 1;
  """
  
  # Execute the query
  response = supabase.query(query)
  
  if response.error is None:
    route_match = response.data
    return route_match
      
  else:
    print(response.error)


def check_capacity(order_data, route_match):
  # create local variables
  route_id = route_match[0]["route_id"]
  closest_pickup = route_match[0]["closest_point_to_p"]
  closest_dropoff = route_match[0]["closest_point_to_d"]
  order_vol = order_data["order_vol"]
  order_weight = order_data["order_weight"]
  coordinates_table = "coordinates"

  # Query to check if route has capacity
  query = f"""
    SELECT empty_vol > {order_vol} AND empty_weight > {order_weight} AS capacity
    FROM {coordinates_table}
    WHERE {route_id} = route_id
      AND ST_Intersects(route_geom, ST_MakeLine({closest_pickup}, {closest_dropoff}))
  """

  # Function and parameters
  function_name = "check_capacity"
  payload = {
      "_order_vol": order_vol,
      "_order_weight": order_weight,
      "_route_id": route_id,
      "_closest_pickup": closest_pickup,
      "_closest_dropoff": closest_dropoff
  }

  # Headers
  headers = {
      "apikey": something.something,
      "Authorization": f"Bearer {something.something}",
      "Content-Type": "application/json"
  }

  # Make the request
  response = requests.post(
      f"{something.url}/rest/v1/rpc/{function_name}",
      headers=headers,
      data=json.dumps(payload)
  )

  # Check response
  if response.status_code == 200:
      result = response.json()
      capacity_available = result.data[0]
      return capacity_available
  else:
      print(f"Error: {response.status_code}")




# pickup and dropoff points come from orders table
def import_route(points):
  """imports all route data from MapBox API

  points: a dict made up of points

  return: If successful, all route data in py converted json format. If failure, print error, return nothing
  """
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
  """checks if order is within area of service

  pick_up, drop_off: lists (lon, lat)

  return: True if yes, False otherwise
  """
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
  """checks if route is one of the standard 5 routes

  route_match: object from supabase query

  return: True if yes, False otherwise
  """
  # create local variables
  route_id = route_match[0]["route_id"]

  if route_id >= 1 and route_id <= 5:
    return True
  else:
    return False

# Tony's functions starts here

def add_order_to_route(route_match, order_data, order_id):
    """adds an order to a given route

    order_id: int -- id of order to add to a route

    return: True if successful, False otherwise
    """
  # Create local variables by parsing route_match + order_data
    route_id = route_match[0]["route_id"]
    closest_pickup = route_match[0]["closest_point_to_p"]
    closest_dropoff = route_match[0]["closest_point_to_p"]
    pickup = order_data["pick_up"]
    dropoff = order_data["drop_off"]

    # Steps to merge pickup and dropoff points into existing route
    # retrieve data from routes table
    route_table_data = supabase.table('routes').select('route_geom', 'points').eq('id', route_id).execute()
    
    if route_table_data.error is None and route_table_data.data:
      route_geom = route_table_data.data[0]['route_geom']
      points = route_table_data.data[0]['points']

    # add closest_pickup and closest_dropoff to points 
    points.extend([closest_pickup, closest_dropoff])

    # call determine_order to get the new list of merged points
    ordered_points = determine_order(points, route_geom)

    # TODO: in ordered_points replace closest_pickup with pickup AND closest_dropoff with dropoff   

    # Update route table
    route_data = update_routes_table(ordered_points, route_id)
    
    # Update capacity table
    update_capacity_table(route_data, ordered_points, route_id)

    # Update orders table  (confirm)
    response = supabase.table('orders').update({'confirmed': True}).eq('id', order_id).execute()

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

    if route_id.error:
      print("Error during insert:", route_id.error)
      return False

    route_id = route_id.data[0]["id"]

    # TODO add route_id to order

    # get new route geom, total time and total distance from mapbox api
    route_data = import_route(points)

    # TODO update routes table
    # TODO update coordinates table


    return route_id


def update_routes_table(ordered_points, route_id):
    """calculates the price of a new order

    ordered_points: list of lists -- all stopping points on route
    route_id: int -- 

    return: If successful, route_data from Mapbox API
    """
    # calculate data
    route_data = import_route(ordered_points)

    # convert time and distance data
    distance_in_meters = route_data['routes'][0]['distance']
    duration_in_seconds = route_data['routes'][0]['duration']
    total_miles = distance_in_meters * 0.000621371 # (1 meter = 0.000621371 miles)
    total_time = duration_in_seconds / 60

    route_row_data = {
      'points': ordered_points,
      'total_miles': total_miles,
      'total_time': total_time
    }

    # update routes table
    response = supabase.tables('routes').update(route_row_data).eq('id', route_id).execute()

    if response.error:
      print("Error during routes table update:", response.error)
      return
    
    return route_data
    

def update_capacity_table(route_data, route_id):
    # create local variables
    route_geom = route_data['routes'][0]['geometry']                                   

    # calculate new volume and weight info


    # insert into 'capacity' table
    capacity_row_data = {
      'route_geom':route_geom,
      'capacity_route_id':route_id
    }
    response = supabase.table('capacity').insert(capacity_row_data).execute()

    if response.error:
      print("Error during insert:", response.error)
    
    # need to update empty_volume and empty_weight in capacity

    return True

def change_capacity(order_data, route_match):
  # create local variables
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

  if response.error is None:
    capacity = response.data
    return capacity
  
  else:
    print(response.error)


def determine_order(points, pickup_loc, dropoff_loc, route_geom):
  #create a new set of points
  return 


def calculate_price(order_id, order_data, route_id):
    """calculates the price of a new order

    order_id: int -- order id to use for calculating price

    return: price as float
    TODO: still need to update package_cost_per_mile data in table
    """
    # query number of packages
    num_packages = supabase.table('orders').select('volume') \
        .eq('id', order_id).execute()
    num_packages = num_packages.data[0]['volume']

    # query pallet cost per mile
    cost_data = supabase.table('costs') \
        .select('package_cost_per_mile', 'markup').execute()
    package_cost_per_mile = cost_data.data[0]['package_cost_per_mile']
    markup = cost_data.data[0]['markup']

    # calculate package distance
    pickup = order_data['pick_up']
    dropoff = order_data['drop_off']

    points = supabase.table('routes').select('points') \
        .eq('id', route_id).execute()

    for point, index in enumerate(points):
        if point == pickup:
            pickup_index = index
        elif point == dropoff:
            dropoff_index = index
            break
    package_points = point[pickup_index : dropoff_index + 1]

    mapbox_data = import_route(package_points)
    distance_meters = mapbox_data['routes'][0]['distance']
    package_miles = distance_meters * METERS2MILES

    return num_packages * package_cost_per_mile * package_miles * (1 + markup)


def is_profitable(route_id):
    """checks to see if a new route is profitable

    route_id: int -- route id to check

    method: query price all orders with route_id
            sum all prices
            calculate OTC of route
            calculate margin

    return: True if profitable, False otherwise
    """
    # get total price of orders on route
    # price_list = supabase.table('orders').select('price') \
    #     .eq('order_route_id', route_id).execute()
    # total_price = sum(price['price'] for price in price_list.data)
    function_name = "calculate_total_price"
    payload = { "_route_id": route_id }

    # Headers
    headers = {
        "apikey": something.something,
        "Authorization": f"Bearer {something.something}",
        "Content-Type": "application/json"
    }

    # Make the request
    response = requests.post(
        f"{something.url}/rest/v1/rpc/{function_name}",
        headers=headers,
        data=json.dumps(payload)
    )

    # Check response
    if response.status_code == 200:
        result = response.json()
        total_price = result.data[0]
    else:
        print(f"Error: {response.status_code}")

    # query route distance
    total_miles = supabase.table('routes').select('id', 'total_miles') \
        .eq('id', route_id).execute()
    total_miles = total_miles.data[0]['total_miles']

    # query cost data
    cost_table_data = supabase.table('costs') \
        .select('total_cost', 'markup').execute()
    total_cost_per_mile = cost_table_data.data[0]['total_cost']
    markup = cost_table_data.data[0]['markup']

    OTC = total_miles * total_cost_per_mile
    margin = (total_price - OTC) / OTC

    return margin > 0


# def calc_total_costs():
#     """Calculate total costs from spreadsheet

#     Total = Trucker + Fuel + Leasing + Maintenance + Insurance

#     return: total cost
#     note: 'costs' table setup wrong direction
#     """
#     # what does the note above mean? RWS
#     # total costs are already calculated in the costs table  RWS


#     trucker = supabase.table('costs').select('trucker_cost').execute()
#     trucker = trucker.data[0]['trucker']

#     fuel = supabase.table('costs').select('fuel_cost').execute()
#     fuel = fuel.data[0]['fuel']

#     leasing = supabase.table('costs').select('leasing_cost').execute()
#     leasing = leasing.data[0]['leasing']

#     maintenance = supabase.table('costs').select('maintenance_cost').execute()
#     maintenance = maintenance.data[0]['maintenance']

#     insurance = supabase.table('costs').select('insurance_cost').execute()
#     insurance = insurance.data[0]['insurance']

#     return trucker + fuel + leasing + maintenance + insurance
