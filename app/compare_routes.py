from flask import Flask, json
from supabase import create_client, Client
import something
from pprint import pprint
from shapely import wkt
import requests

METERS2MILES = 0.000621371
TOTAL_TRUCK_VOLUME = 1700   # cubic feet
TOTAL_TRUCK_WEIGHT = 9180   # pounds
STD_PACKAGE_VOL = 18
PALLET_VOL = 64
HEADERS = { 
    "apikey": something.something, 
    "Authorization": f"Bearer {something.something}",
        "Content-Type": "application/json"
    }

app = Flask(__name__)

supabase = create_client(something.url, something.something)
  
  
def process_order(order_id, order_data):
    # create local variables
    order_table = "orders"
    price = 0
    route_id = 0

    # check if order fits on an existing route
    route_info = compare_routes(order_data)   

    # if route match is found
    if route_info:
        route_match = route_info["route_match"]
        coord_data = route_info["coord_data"]
        # add route_id to order
        route_id = route_match[0]["route_id"]
        try:
            print("Line 32")
            order_update = supabase.table(order_table).update({"order_route_id": route_id}).eq("id", order_id).execute()
        except:
            print(f"process_order: table could not be updated")
            exit(1)

        # add order to route
        coord_data = add_order_to_route(order_id, order_data, route_id, coord_data)
        order_point_subset = coord_data["order_point_subset"]

        # calculate price
        price = calculate_price(order_id, order_point_subset)

        # if is_original, return price
        if is_original(route_id):
            return price
        # else check profitability
        else:
            if is_profitable(route_id):
                # TODO return price for every order in route
                return price
            else:
                print("No profitable route found, order stored for future")
                return None

  # if there is no match, create a new route and check whether the route is profitable
    else: 
        # create new route
        new_route_data = create_new_route(order_id, order_data)
        route_id = new_route_data["route_id"]
        points = new_route_data["points"]

        # calculate price
        price = calculate_price(order_id, points)

        # check profitability
        if (is_profitable(route_id)):
            print(f"New profitable route found, route_id {route_id}.")
        else:
            print("No profitable route found, order stored for future")
    
    return price

# pickup and dropoff points come from orders table
def import_route(points):
    """imports all route data from MapBox API

    points: a dict made up of points

    return: If successful, all route data in py converted json format. If failure, print error, return nothing
    """
    # Mapbox public token
    access_token = "pk.eyJ1IjoicnN3aGlwcGxlIiwiYSI6ImNsb2RlbnN0eTA2bnoyaXQ4aWc1YmF0eGgifQ.nVC4l7HRRRiAYT-A_4ySuA"

    # Convert each point into a string (longitude, latitude) format
    coordinates = '%3B'.join(f'{lon}%2C{lat}' for lon, lat in points)
    
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
    

def compare_routes(order_data):
    # create local variables
    pickup = order_data["pickup"]
    dropoff = order_data["dropoff"]

    # create pickup and dropoff points ON EXISTING ROUTES
    route_match = check_points(pickup, dropoff)

    if route_match:
        coord_data = check_capacity(order_data, route_match)

        if coord_data:
            route_info = {
                "route_match": route_match,
                "coord_data": coord_data
            }
            return route_info
        else:
            return None
    else:
        return None
    
  
# pickup and dropoff points come from orders table
def check_points(pickup, dropoff):
    # create local variables
    routes_table = "routes"

    # convert points to Well Known Text (WKT)
    pickup_wkt = convert_tuple_to_wkt(pickup)
    dropoff_wkt = convert_tuple_to_wkt(dropoff)

    # Function and parameters
    function_name = "check_points"
    payload = {
        "_pickup": pickup_wkt,
        "_dropoff": dropoff_wkt
    }

    # Make the request
    response = requests.post(
        f"{something.url}/rest/v1/rpc/{function_name}",
        headers=HEADERS,
        data=json.dumps(payload)
    )

    # Check response
    if response.status_code == 200:
        result = response.json()
        route_match = result.data[0]
        return route_match
    else:
        print(f"check_points: {response.status_code}")
        exit(1)


def check_capacity(order_data, route_match):
    # create local variables
    route_id = route_match[0]["route_id"]
    order_vol = order_data["order_vol"]
    order_weight = order_data["order_weight"]

    # create list of points on route [point before pickup: point before dropoff + 1]
    coord_data = find_coord_data(route_match)
    points = coord_data["order_point_subset"]


    # Function and parameters
    function_name = "check_capacity"
    payload = {
        "_order_vol": order_vol,
        "_order_weight": order_weight,
        "_route_id": route_id,
        "_wkt_points": points
    }

    # Make the request
    response = requests.post(
        f"{something.url}/rest/v1/rpc/{function_name}",
        headers=HEADERS,
        data=json.dumps(payload)
    )

    # Check response
    if response.status_code == 200:
        result = response.json()
        capacity_available = result.data[0]
        if capacity_available:
            return coord_data
        else:
            return None
    else:
        print(f"check_capacity: {response.status_code}")


def find_coord_data(route_match):
    """
    find point before closest_point_p and point after closest_point_d
    create a list of all points inbetween these 2 points (inclusive)
    """
    route_id = route_match[0]["route_id"]
    closest_point_pickup = route_match[0]["closest_point_p"]
    closest_point_dropoff = route_match[0]["closest_point_d"]

    # retrieve route_id points from supabase
    try:
        print("Line 679")
        result = supabase.table('routes').select('points').eq('id', route_id).execute()
        points = result.data[0]['points']
    except:
        print("find_coords: Error retrieving points with route_id: ", route_id)
        exit(1)

    # find index_a, point before closest_point_pickup
    point_a = find_point_before(route_id, closest_point_pickup, points)

    # find index_b, point after closest_point_dropoff
    point_b = find_point_before(route_id, closest_point_dropoff, points)
    
    # return list of all points between index_a and index_b inclusive
    point_subset = points_between(points, point_a, point_b)

    coord_data = {
        "route_points": points,
        "order_point_subset": point_subset,
        "point_before_pickup": point_a,
        "point_before_dropoff": point_b
    }

    return coord_data


def is_in_range(pickup, dropoff):
    """checks if order is within area of service

    pick_up, drop_off: lists (lon, lat)

    return: True if yes, False otherwise
    """
    # Set variable for 
    home_base = (-84.3875298776525, 33.754413815792205)

    points = [home_base, pickup, dropoff, home_base]

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

def add_order_to_route(order_id, order_data, route_id, coord_data):
    """adds an order to a given route

    order_id: int -- id of order to add to a route

    return: True if successful, False otherwise
    """
    # Create local variables 
    pickup = order_data["pickup"]
    dropoff = order_data["dropoff"]
    point_before_pickup = coord_data["point_before_pickup"]
    point_before_dropoff = coord_data["point_before_dropoff"]
    points = coord_data["route_points"]

    # Insert pickup and dropoff into correct position in point list
    index_a = points.index(point_before_pickup)
    points.insert(index_a + 1, pickup)

    index_b = points.index(point_before_dropoff)
    points.insert(index_b + 1, dropoff)

    coord_data["route_points"] = points
    coord_data["order_point_subset"] = points[points.index(pickup): points.index(dropoff) + 1]

    # Update route table
    # question + do we need the route_data?
    update_routes_table(points, route_id)
    
    # Insert new points in coordinates table
    insert_coord_existing_route(route_id, order_data, pickup, point_before_pickup) 
    insert_coord_existing_route(route_id, order_data, dropoff, point_before_dropoff) 

    # Update empty_vol and empty_weight in coordinates table
    update_coordinates_table(route_id, order_data, coord_data)

    # Update orders table  (confirm)
    try:
        print("Line 284")
        response = supabase.table('orders').update({'confirmed': True}).eq('id', order_id).execute()
    except:
        print("add_order_to_route: update of orders table failed")
        exit(1)

    return coord_data


def create_new_route(order_id, order_data):
    """creates a new route in database

    order_id: int -- order id for needing new route
    order_data: dict -- data of order for new route

    return: id of new route created
    """
    # build new route
    home_base= (-84.3875298776525, 33.754413815792205)
    points = [home_base, order_data["pickup"], order_data["dropoff"], home_base]
    new_route = {"points": points}

    # insert into 'routes' table
    try:
        print("Line 308")
        route_id = supabase.table('routes').insert(new_route).execute()
    except:
        print("create_new_route: insert of new_route failed in table routes")
        exit(1)

    route_id = route_id.data[0]["id"]

    # add route_id to order
    try:
        print("Line 319")
        response = supabase.table('orders').update({'order_route_id': route_id}).eq('id', order_id).execute()
    except:
        print("create_new_route: update of orders table failed")
        exit(1)

    # update routes table
    update_routes_table(points, route_id)

    # create new rows in coordinates table with correct data
    insert_coord_new_route(route_id, points, order_data)

    new_route_data = {
        "route_id": route_id,
        "points": points
    }

    # create new row in margins table with margin_route_id
    # try:
    #     print("Line 333")
    #     response = supabase.table('margins').insert({'margin_route_id': route_id}).execute()
    # except:
    #     print("create_new_route: Error creating margins table row for new route")
    #     exit(1)

    return new_route_data


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
        print("Line 369")
        response = supabase.tables('routes').update(route_row_data).eq('id', route_id).execute()
    except:
        print("update_routes_table: Error during routes table update")
        exit(1)

    return route_data
    

def update_coordinates_table(route_id, order_data, coord_data):
    # create local variables
    pickup = order_data['pickup']
    dropoff = order_data['dropoff']

    # find affected points
    package_points = coord_data["order_point_subset"]

    for point in package_points:
        # get current volume and weight data
        try:
            print("Line 389")
            coord_data = supabase.table('coordinates').select('*') \
                .eq('point', point).eq('coordinate_route_id', route_id).execute()
        except:
            print("update_coordinates_table: coordinates table cannot select *")
            exit(1)

        current_empty_vol = coord_data.data[0]['empty_vol']
        current_empty_weight = coord_data.data[0]['empty_weight']

        # calculate new volume and weight available
        empty_vol = current_empty_vol - order_data['order_vol']
        empty_weight = current_empty_weight - order_data['order_weight']

        # insert into 'coordinates' table
        coordinates_row_data = {
            'point': point,
            'empty_vol': empty_vol,
            'empty_weight': empty_weight
        }

    try:
        print("Line 411")
        response = supabase.table('coordinates').update(coordinates_row_data) \
              .eq('point', point).eq('coordinate_route_id', route_id).execute()
    except:
        print("update_coordinates_table: coordinates table cannot insert")
        exit(1)

    return True


def insert_coord_new_route(route_id, points, order_data):
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
        print("Line 475")
        response = supabase.table('coordinates').insert(coordinates_row_data).execute()
    except:
        print("insert_coordinates_table: Error during insert")
        exit(1)

    return True


def insert_coord_existing_route(route_id, order_data, point, point_before):
    # calculate empty_vol and empty_weight for pickup
    try:
        print("Line 487")
        capacity_data = supabase.table('coordinates').select('empty_vol', 'empty_weight') \
                .eq('coordinate_route_id', route_id).eq('point', point_before).execute()
    except:
        print("insert_coord_existing_route(): Error during select")
        exit(1)
    
    current_vol = capacity_data.data[0]['empty_vol']
    current_weight = capacity_data.data[0]['empty_weight']
    # weight per/package * num packages
    if order_data["package_type"] == 'standard':
        total_order_vol = STD_PACKAGE_VOL * order_data['order_vol']
        empty_vol = current_vol - total_order_vol
        total_order_weight = order_data['weight']   # make sure total weight is provided
        empty_weight = current_weight - total_order_weight

    # transform points into rows for table
    coordinates_row_data = {
        'point': point,
        'empty_vol': empty_vol,
        'empty_weight': empty_weight,
        'coordinate_route_id': route_id
    }
    try:
        print("Line 440")
        response = supabase.table('coordinates').insert(coordinates_row_data).execute()
    except:
        print("insert_coord_existing_route(): Error during insert")
        exit(1)

    return True


def calculate_price(order_id, order_point_subset):
    """calculates the price of a new order

    order_id: int -- order id to use for calculating price

    return: price as float
    """
    # query number of packages
    try:
        print("Line 526")
        num_packages = supabase.table('orders').select('volume') \
            .eq('id', order_id).execute()
    except:
        print("calculate_price: orders table cannot select volume")
        exit(1)

    num_packages = num_packages.data[0]['volume']

    # query pallet cost per mile and markup
    try:
        print("Line 537")
        cost_data = supabase.table('costs') \
            .select('package_cost_per_mile', 'markup').execute()
    except:
        print("calculate_price: costs table cannot sellect package_cost_per_mile or markup")
        exit(1)

    package_cost_per_mile = cost_data.data[0]['package_cost_per_mile']
    markup = cost_data.data[0]['markup']

    # calculate package distance
    mapbox_data = import_route(order_point_subset)
    distance_meters = mapbox_data['routes'][0]['distance']
    package_miles = distance_meters * METERS2MILES

    # calculate price
    price = num_packages * package_cost_per_mile * package_miles * (1 + markup)

    # update order_id with price
    try:
        print("Line 570")
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
    # Function name and parameters
    function_name = "calculate_total_price"
    payload = { "_route_id": route_id }

    # Make the request
    response = requests.post(
        f"{something.url}/rest/v1/rpc/{function_name}",
        headers=HEADERS,
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
        print("Line 618")
        total_miles = supabase.table('routes').select('id', 'total_miles') \
            .eq('id', route_id).execute()
    except:
        print("is_profitable: routes table cannot select id or total_miles")
        exit(1)

    total_miles = total_miles.data[0]['total_miles']

    # query cost data
    try:
        print("Line 629")
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
        print("Line 651")
        result = supabase.table('margins').update(margins_row_data).eq('margin_route_id', route_id).execute()
    except:
        print("is_profitable: Error updating margins table for route: ", route_id)
        exit(1)

    return margin > 0


def points_between(points, point_a, point_b):
    try:
        index_a = points.index(point_a)
        index_b = points.index(point_b)

        return points[index_a: index_b + 1]
    except:
        # value error 
        return []


def find_point_before(route_id, point_list, point):
    # convert point_list to WKT
    for point in point_list:
        point = convert_tuple_to_wkt(point)

    # Supabase function name and parameters
    function_name = "point_before"
    payload = {
        "_route_id": route_id,
        "_point": point,
        "_point_list": point_list,
    }

    # Make the request
    response = requests.post(
        f"{something.url}/rest/v1/rpc/{function_name}",
        headers=HEADERS,
        data=json.dumps(payload)
    )

    # Check response
    if response.status_code == 200:
        result = response.json()
        point_before = result.data
        point_before = convert_geom_to_tuple(point_before)
    else:
        print(f"Error in find_point_before(): {response.status_code}")
    
    return point_before

def convert_tuple_to_wkt(lon_lat_tuple):
    # Convert tuple to WKT format
    return f"POINT({lon_lat_tuple[0]} {lon_lat_tuple[1]})" # Example Output: POINT(-73.935242 40.730610)


def convert_geom_to_tuple(geometry_point):
    # Convert WKT to a shapely Point object
    point = wkt.loads(geometry_point)

    # Convert the Point to a tuple (longitude, latitude)
    return (point.x, point.y)








# def find_point_after(route_id, point_list, point):
#     # convert point_list to WKT
#     for point in point_list:
#         point = convert_tuple_to_wkt(point)

#     # Supabase function name
#     function_name = "point_after"
#     payload = {
#         "_route_id": route_id,
#         "_point": point,
#         "point_list": point_list
#     }

#     # Make the request
#     response = requests.post(
#         f"{something.url}/rest/v1/rpc/{function_name}",
#         headers=HEADERS,
#         data=json.dumps(payload)
#     )

#     # Check response
#     if response.status_code == 200:
#         result = response.json()
#         point_after = result.data
#         point_after = convert_geom_to_tuple(point_after)
#     else:
#         print(f"Error in find_point_before(): {response.status_code}")
    
#     return point_after
