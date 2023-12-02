from flask import Flask, json
from supabase import create_client, Client
import something
import compare_routes
from pprint import pprint
import requests

app = Flask(__name__)

supabase = create_client(something.url, something.something)

def update_original_routes():
    # route data
    route_data = {
        "1": (-85.1103924702221, 34.9161210050057),
        "2": (-81.8920767938344, 33.4676716195606),
        "3": (-80.9773396382228, 32.0815296895872),
        "4": (-84.1807668794164, 31.5770410650746),
        "5": (-85.1587927831466, 32.4661710120819),
    }
    # build new route
    home_base = (-84.3875298776525, 33.754413815792205)

    for index in range(1, 6):
        route_id = index
        points = [home_base, route_data[f"{index}"], home_base]

        route_row_data = {
            'id': route_id,
            'points': points
        }
        print(route_row_data)

        try:
            updated_route = supabase.table('routes').update(route_row_data) \
                .eq('id', route_id).execute()
        except:
            print(f"update original routes: table could not be updated")
            exit(1)




