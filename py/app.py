from flask import Flask, request, jsonify
from supabase import create_client, Client
import something
from pprint import pprint
from compare_routes import *

app = Flask(__name__)

supabase = create_client(something.url, something.something)

# Function to Fetch All Orders
def find_all_orders():
    response = supabase.table('orders').select("*").execute()
    # Equivalent for SQL Query "SELECT * FROM orders;"
    return response.data

@app.route('/')
def index():
    orders = find_all_orders()
  
    # print to console
    pprint(orders)
    # print to frontend
    return f'{orders}'


@app.route('/receive_order', methods=['POST'])
def add_order_database():
    # Check if the request contains JSON data
    if request.is_json:
        try:
            data = request.get_json()

            # Access specific data from the JSON input
            cargo = data.get("cargo", {})
            packages = cargo.get("packages", [])
            pick_up = data.get("pick-up", {})   # make sure format is (lon, lat)
            drop_off = data.get("drop-off", {})

            volume, weight, package_type = packages
            # pick_up = (pick_up.get("longitude", 0), pick_up.get("latitude", 0))
            # drop_off = (drop_off.get("longitude", 0), drop_off.get("latitude", 0))

            # Process the data or return a response as needed
            response_data = {
                "volume": volume,
                "weight": weight,
                "package_type": package_type,
                "pick_up": pick_up,
                "drop_off": drop_off,
                "in_range": True,
            }

            # Add items to database
            response = supabase.table('orders').insert(response_data).execute()

            # Get order_id from response
            order_id = response.data[0]["id"]

            # Check if order is in range
            range = is_in_range(pick_up, drop_off)

            if not range:
                # Update order in database and return error if out of range
                response = supabase.table('orders').update({"in_range": False}).eq("id", order_id).execute()
                return jsonify({"error": "Order is out of range"})

            # Process order
            process_order(order_id, response_data)

            return jsonify(response_data) # this will need to be changed

        except Exception as e:
            return jsonify({"error": "Invalid input format or processing error"})
    else:
        return jsonify({"error": "Invalid request format (JSON expected)"})


if __name__ == '__main__':
  app.run()


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    # Check if the request contains JSON data
    if request.is_json:
        try:
            data = request.get_json()

            # Access specific data from the JSON input
            order_id = data.get("order_id", 0)

            # Add order to the routes table

            # Update order status to confirmed


            return jsonify(response_data) # this will need to be changed

        except Exception as e:
            return jsonify({"error": "Invalid input format or processing error"})
    else:
        return jsonify({"error": "Invalid request format (JSON expected)"})
    
