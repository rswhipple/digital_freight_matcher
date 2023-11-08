from dotenv import load_dotenv
load_dotenv()

# from flask import Flask, request, jsonify
# import something
# from pprint import pprint

# app = Flask(__name__)

from classes import *

import os

from supabase import create_client

import json

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# @app.route('/update_costs', methods=['POST'])
def update_costs_table(data):

  costs_table = "costs"
  id = 1

  # update database costs table with new costs
  data_dict = json.loads(data)

  if 'trucker_cost' in data_dict:
    data = supabase.table(costs_table).update({"trucker_cost": data_dict['trucker_cost']}).eq("id", 1).execute()
  if 'leasing_cost' in data_dict:
    data = supabase.table(costs_table).update({"leasing_cost": data_dict['leasing_cost']}).eq("id", 1).execute()
  if 'maintenance_cost' in data_dict:
    data = supabase.table(costs_table).update({"maintenance_cost": data_dict['maintenance_cost']}).eq("id", 1).execute()
  if 'insurance_cost' in data_dict:
    data = supabase.table(costs_table).update({"insurance_cost": data_dict['insurance_cost']}).eq("id", 1).execute()
  if 'gas_price' and 'miles_gallon' in data_dict:
    data = supabase.table(costs_table).update({"gas_price": data_dict['gas_price'], "miles_gallon": data_dict['miles_gallon'], "fuel_cost": data_dict['gas_price'] / data_dict['miles_gallon']}).eq("id", 1).execute()

  current = supabase.table("costs").select("*").execute()
  # Assert we pulled real data.
  assert len(data.data) > 0

  if 'gas_price' in data_dict and 'miles_gallon' not in data_dict:
    data = supabase.table(costs_table).update({"gas_price": data_dict['gas_price'], "fuel_cost": data_dict['gas_price'] / current['miles_gallon']}).eq("id", 1).execute()

  # update total cost
  data = supabase.table(costs_table).update({"total_cost": current['trucker_cost'] + current['leasing_cost'] + current['maintenance_cost'] + current['insurance_cost'] + current['fuel_cost']}).eq("id", 1).execute()
