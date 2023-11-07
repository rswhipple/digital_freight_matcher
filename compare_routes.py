# CREATE TABLE routes (
#    id serial PRIMARY KEY,
#    points geometry(MultiPoint, 4326)
#    total_time integer,
#    total_miles integer,
# );

from dotenv import load_dotenv
load_dotenv()

from classes import *

import os

from supabase import create_client

import json

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

def compare_routes(order_id):
  # get pickup and dropoff points from orders table
  order_table = "orders" 
  query = f"""
    SELECT pickup, drop_off, order_vol, order_weight
    FROM {order_table}
    WHERE id = {order_id};
    """
  
  # Execute the query
  response = supabase.query(query)

  if response.status_code == 200:
    order = response.get("data")
    pickup = order[0]["pickup"]
    drop_off = order[0]["drop_off"]

    results = check_points(pickup, drop_off)

    if results:
      capacity = check_capacity(order, results)

      if capacity:
        route_id = capacity[0]["route_id"]
        return route_id
      else:
        return None
    else:
      return None
    
  else:
    print(response.error)
  
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
    results = response.get("data")
    return results
      
  else:
    print(response.error)


def check_capacity(order, results):
  route_id = results[0]["route_id"]
  pickup = results[0]["pickup"]
  drop_off = results[0]["drop_off"]
  order_vol = order[0]["order_vol"]
  order_weight = order[0]["order_weight"]

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