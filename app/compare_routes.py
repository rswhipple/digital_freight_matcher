from flask import Flask, json
from supabase import create_client, Client
import something
from pprint import pprint
import requests

METERS2MILES = 0.000621371
TOTAL_TRUCK_VOLUME = 1700   # cubic feet
TOTAL_TRUCK_WEIGHT = 9180   # pounds
STD_PACKAGE_VOL = 18
PALLET_VOL = 64

app = Flask(__name__)

supabase = create_client(something.url, something.something)
  
  
def process_order(order_id, order_data):
  # create local variables
  order_table = "orders"
  price = 0
  route_id = 0

  # check if order fits on an existing route
  route_match = compare_routes(order_data)   

  # if route match is found
  if route_match:
    # add route_id to order
    route_id = route_match[0]["route_id"]
   try:
           order_update = supabase.table(order_table).update({"order_route_id": route_id}).eq("id", order_id).execute()
   except:
       print(f"process_order: table could not be updated")
       exit(1)

    assert len(order_update.data) > 0, "Error: Unable to update orders table with route_id"

    # add order to route
    add_order_to_route(order_id, order_data, route_match)

    # if route is_original() calculate price 
    if is_original(route_id):
      price = calculate_price(order_id, order_data, route_id)
    # else check if it is profitable before calculating price
    else:
      if is_profitable(route_id):
        price = calculate_price(order_id, order_data, route_id)
        # TODO calculate price for every order in route
      else:
        print("No profitable route found, order stored for future")
  
  # if there is no match, create a new route and check whether the route is profitable
  else: 
    route_id = create_new_route(order_id)
    results = is_profitable(route_match) 
    if results:
      # calculate price
      price = calculate_price(order_id, order_data, route_id)
      print(f"New profitable route found, route_id {route_id}.")
    else:
      print("No profitable route found, order stored for future")
  
  return price
    

def compare_routes(order_data):
  # create local variables
  pickup = order_data["pickup"]
  dropoff = order_data["dropoff"]

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

  # Function and parameters
  function_name = "check_points"
  payload = {
      "_pickup": pickup,
      "_dropoff": dropoff
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
      route_match = result.data[0]
      return route_match
  else:
      print(f"Error: {response.status_code}")


def check_capacity(order_data, route_match):
  # create local variables
  route_id = route_match[0]["route_id"]
  closest_pickup = route_match[0]["closest_point_to_p"]
  closest_dropoff = route_match[0]["closest_point_to_d"]
  order_vol = order_data["order_vol"]
  order_weight = order_data["order_weight"]
  coordinates_table = "coordinates"

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
  
def is_original(route_id):
  """checks if route is one of the standard 5 routes

  route_match: object from supabase query

  return: True if yes, False otherwise
  """
  if route_id >= 1 and route_id <= 5:
    return True
  else:
    return False

# Tony's functions starts here

def add_order_to_route(order_id, order_data, route_match):
    """adds an order to a given route

    order_id: int -- id of order to add to a route

    return: True if successful, False otherwise
    """
  # Create local variables by parsing route_match + order_data
    route_id = route_match[0]["route_id"]
    closest_pickup = route_match[0]["closest_point_to_p"]
    closest_dropoff = route_match[0]["closest_point_to_p"]
    pickup = order_data["pickup"]
    dropoff = order_data["dropoff"]

    # Steps to merge pickup and dropoff points into existing route
    # retrieve data from routes table
   try:
           route_table_data = supabase.table('routes').select('route_geom', 'points').eq('id', route_id).execute()
   except:
       print("add_order_to_route: route_geom and points not found in routes")
       exit(1)

    
    if route_table_data.error is None and route_table_data.data:
      route_geom = route_table_data.data[0]['route_geom']
      points = route_table_data.data[0]['points']

    # add closest_pickup and closest_dropoff to points 
    points.extend([closest_pickup, closest_dropoff])

    # call determine_order to get the new list of merged points
    ordered_points = determine_order(points, route_geom)

    # in ordered_points replace closest_pickup with pickup AND closest_dropoff with dropoff 
    for point in ordered_points:
      if point == closest_pickup:
        point = pickup
      elif point == closest_dropoff:
        point =  dropoff

    # Update route table
    # question + do we need the route_data?
    update_routes_table(ordered_points, route_id)
    
    # Update coordinates table
    update_coordinates_table(route_id, ordered_points, order_id, order_data)

    # Update orders table  (confirm)
   try:
           response = supabase.table('orders').update({'confirmed': True}).eq('id', order_id).execute()
   except:
       print("add_order_to_route: update of orders table failed")
       exit(1)


    return True


def create_new_route(order_id, order_data):
    """creates a new route in database

    order_id: int -- order id for needing new route
    order_data: dict -- data of order for new route

    return: id of new route created
    """
    # build new route
    home_base = (-84.3875298776525, 33.754413815792205)
    points = [home_base, order_data["pickup"], order_data["dropoff"], home_base]
    new_route = {"points": points}

    # insert into 'routes' table
   try:
           route_id = supabase.table('routes').insert(new_route).execute()
   except:
       print("create_new_route: insert of new_route failed in table routes")
       exit(1)


    if route_id.error:
      print("Error during insert:", route_id.error)
      return False

    route_id = route_id.data[0]["id"]

    # add route_id to order
   try:
           response = supabase.table('orders').update({'order_route_id': route_id}).eq('id', order_id).execute()
   except:
       print("create_new_route: update of orders table failed")
       exit(1)

    # update routes table
    update_routes_table(points, route_id)

    # create new rows in coordinates table with correct data
    insert_coordinates_table(route_id, points, order_data)

    # create new row in margins table with margin_route_id
   try:
           response = supabase.table('margins').insert({'margin_route_id': route_id}).execute()
   except:
       print("create_new_route: Error creating margins table row for new route")
       exit(1)

    return route_id


def update_routes_table(ordered_points, route_id):
    """calculates the price of a new order

    ordered_points: list of lists -- all stopping points on route
    route_id: int -- 

    return: If successful, route_data from Mapbox API
    """
    # calculate data
    route_data = import_route(ordered_points)
    route_geom = route_data['routes'][0]['route_geom']

    # convert time and distance data
    distance_in_meters = route_data['routes'][0]['distance']
    duration_in_seconds = route_data['routes'][0]['duration']
    total_miles = distance_in_meters * METERS2MILES # (1 meter = 0.000621371 miles)
    total_time = duration_in_seconds / 60

    route_row_data = {
      'route_geom': route_geom,
      'points': ordered_points,
      'total_miles': total_miles,
      'total_time': total_time
    }

    # update routes table
   try:
           response = supabase.tables('routes').update(route_row_data).eq('id', route_id).execute()
   except:
       print("update_routes_table: Error during routes table update:", response.error)
       exit(1)

    return route_data
    

def update_coordinates_table(route_id, ordered_points, order_id, order_data):
    # create local variables
    pickup = order_data['pickup']
    dropoff = order_data['dropoff']

    # find affected points
    package_points = order_package_points(ordered_points, pickup, dropoff)

    for point in package_points:
      # get current volume and weight data
   try:
             coord_data = supabase.table('coordinates').select('*') \
            .eq('point', point).eq('coordinate_route_id', route_id).execute()
   except:
       print("update_coordinates_table: coordinates table cannot select *")
       exit(1)

       current_empty_vol = coord_data.data[0]['empty_vol']
       current_empty_weight = coord_data.data[0]['empty_weight']

      # calculate new volume and weight available
      empty_vol = current_empty_vol - order_data['order_vol']

      # insert into 'coordinates' table
      coordinates_row_data = {
        'point': point
      }
   try:
         response = supabase.table('coordinates').insert(coordinates_row_data).execute()
   except:
       print("update_coordinates_table: coordinates table cannot insert")
       exit(1)

    return True

def insert_coordinates_table(route_id, points, order_data):
    # calculate empty_vol and empty weight
    # weight per/package * num packages
    if order_data["package_type"] == 'standard':
      total_order_vol = STD_PACKAGE_VOL * order_data['order_vol']
      empty_vol = TOTAL_TRUCK_VOLUME - total_order_vol
      total_order_weight = order_data['weight']   # make sure total weight is provided
      empty_weight = TOTAL_TRUCK_WEIGHT - total_order_weight

    # transform points into rows for table
    for point in points:
      # insert into 'coordinates' table
      coordinates_row_data = {
        'point': point,
        'empty_vol': empty_vol,
        'empty_weight': empty_weight,
        'coordinate_route_id': route_id
      }
   try:
             response = supabase.table('coordinates').insert(coordinates_row_data).execute()
   except:
       print("insert_coordinates_table: Error during insert:", response.error)
       exit(1)

    return True


def determine_order(points, pickup_loc, dropoff_loc, route_geom):
  # create a new set of points
  ordered_points = []

  # for each point, check if pickup_loc comes before point, 
  #   if no, add point
  #   if yes, add pickup_loc before adding point

  # for each point, check if dropoff_loc comes before point, 
  #   if no, add point
  #   if yes, add dropoff_loc before adding point

  return ordered_points


def calculate_price(order_id, order_data, route_id):
    """calculates the price of a new order

    order_id: int -- order id to use for calculating price

    return: price as float
    """
    # query number of packages
   try:
           num_packages = supabase.table('orders').select('volume') \
        .eq('id', order_id).execute()
   except:
       print("calculate_price: orders table cannot select volume")
       exit(1)

    num_packages = num_packages.data[0]['volume']

    # query pallet cost per mile and markup
   try:
           cost_data = supabase.table('costs') \
        .select('package_cost_per_mile', 'markup').execute()
   except:
       print("calculate_price: costs table cannot sellect package_cost_per_mile or markup")
       exit(1)

    package_cost_per_mile = cost_data.data[0]['package_cost_per_mile']
    markup = cost_data.data[0]['markup']

    # calculate package distance
    pickup = order_data['pick_up']
    dropoff = order_data['drop_off']

   try:
           points = supabase.table('routes').select('points') \
        .eq('id', route_id).execute()
   except:
       print("calculate_price: routes table cannot select points")
       exit(1)

    package_points = order_package_points(points, pickup, dropoff)

    mapbox_data = import_route(package_points)
    distance_meters = mapbox_data['routes'][0]['distance']
    package_miles = distance_meters * METERS2MILES

    # calculate price
    price = num_packages * package_cost_per_mile * package_miles * (1 + markup)

    # update order_id with price
   try:
           response = supabase.table('orders').update({'price': price}).eq('id', order_id).execute()
   except:
       print("calculate_price: orders table cannot update price")
       exit(1)

    return price


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
   try:
           total_miles = supabase.table('routes').select('id', 'total_miles') \
        .eq('id', route_id).execute()
   except:
       print("is_profitable: routes table cannot select id or total_miles")
       exit(1)

    total_miles = total_miles.data[0]['total_miles']

    # query cost data
   try:
           cost_table_data = supabase.table('costs') \
        .select('total_cost', 'markup').execute()
   except:
       print("is_profitable: costs table cannot select total_cost or markup")
       exit(1)

    total_cost_per_mile = cost_table_data.data[0]['total_cost']
    markup = cost_table_data.data[0]['markup']

    # calculate OTC (operational truck cost) and margin
    OTC = total_miles * total_cost_per_mile
    margin = (total_price - OTC) / OTC

    # update margins table
    margins_row_data = {
       'margin': margin,
       'operational_cost': OTC,
       'income': total_price
    }

   try:
        result = supabase.table('margins').update(margins_row_data).eq('margin_route_id', route_id).execute()
   except:
       print("is_profitable: Error updating margins table for route: ", route_id)
       exit(1)

    return margin > 0

def order_package_points(points, pickup, dropoff):
  for point, index in enumerate(points):
    if point == pickup:
      pickup_index = index
    elif point == dropoff:
      dropoff_index = index
      break

  package_points = point[pickup_index : dropoff_index + 1]

  return package_points

