from flask import Flask, json
from supabase import create_client, Client
import something
from pprint import pprint
import requests

app = Flask(__name__)

supabase = create_client(something.url, something.something)

def update_original_routes():
    # route data
    route_data = {
        "1": (-84.3875298776525, 33.754413815792205),
        "2": (-85.11039247022218, 34.9161210050057),
        "3": (-80.9773396382228, 33.4676716195606),
        "4": (80.9773396382228, ),
        "5": (volume),
    }
    # build new route
    home_base = (-84.3875298776525, 33.754413815792205)

    for index in range(1, 6):
        route_id = {index}
        points = [home_base, route_data["{index}"], home_base]

        route_row_data = {
            'id': route_id,
            'points': points
        }

        try:
            updated_route = supabase.table('routes').update(route_row_data) \
                .eq('id', route_id).execute()
        except:



