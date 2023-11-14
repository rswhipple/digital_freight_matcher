from flask import Flask, request, jsonify
from supabase import create_client, Client
import something
from pprint import pprint
from compare_routes import *

app = Flask(__name__)

supabase = create_client(something.url, something.something)

@app.route('/update_costs', methods=['POST'])
def update_costs_table(data):

  if request.is_json:
    data = request.get_json()

    # Access specific data from the JSON input
    trucker_cost = data.get("trucker_cost", {})
    leasing_cost = data.get("leasing_cost", [])
    maintenance_cost = data.get("maintenance_cost-up", {})   
    insurance_cost = data.get("insurance_cost", {})
    gas_price = data.get("gas_price", {})
    miles_gallon = data.get("miles_gallon", {})

    costs_table = "costs"
    id = 1

    if trucker_cost:
        data = supabase.table(costs_table).update({"trucker_cost": trucker_cost}).eq("id", 1).execute()
    if leasing_cost:
        data = supabase.table(costs_table).update({"leasing_cost": leasing_cost}).eq("id", 1).execute()
    if maintenance_cost:
        data = supabase.table(costs_table).update({"maintenance_cost": maintenance_cost}).eq("id", 1).execute()
    if insurance_cost:
        data = supabase.table(costs_table).update({"insurance_cost": insurance_cost}).eq("id", 1).execute()
    if gas_price and miles_gallon:
        data = supabase.table(costs_table).update({"gas_price": gas_price, "miles_gallon": miles_gallon, "fuel_cost": gas_price / miles_gallon}).eq("id", 1).execute()

    current = supabase.table("costs").select("*").execute()
    # Assert we pulled real data.
    assert len(data.data) > 0

    if gas_price and not miles_gallon:
        data = supabase.table(costs_table).update({"gas_price": gas_price, "fuel_cost": gas_price / current['miles_gallon']}).eq("id", 1).execute()

    # update total cost
    data = supabase.table(costs_table).update({"total_cost": current['trucker_cost'] + current['leasing_cost'] + current['maintenance_cost'] + current['insurance_cost'] + current['fuel_cost']}).eq("id", 1).execute()
