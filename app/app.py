from flask import Flask, request, jsonify
from supabase import create_client, Client
# import schedule
# import time
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
            pickup = data.get("pick-up", {})   # make sure format is (lon, lat) ******************  this may cause error
            dropoff = data.get("drop-off", {})
            volume, weight, package_type = packages
            # pick_up = (pick_up.get("longitude", 0), pick_up.get("latitude", 0))
            # drop_off = (drop_off.get("longitude", 0), drop_off.get("latitude", 0))

            # Process the data or return a response as needed
            order_data = {
                "volume": volume,
                "weight": weight,
                "package_type": package_type,
                "pickup": pickup,
                "dropoff": dropoff,
                "in_range": True,
            }

            # Add items to database
            response = supabase.table('orders').insert(order_data).execute()

            # Get order_id from response
            order_id = response.data[0]["id"]

            # Check if order is in range
            range = is_in_range(pickup, dropoff)

            if not range:
                # Update order in database and return error if out of range
                response = supabase.table('orders').update({"in_range": False}).eq("id", order_id).execute()
                return jsonify({"error": "No possible routes, order is out of range"})

            # Process order
            price = process_order(order_id, order_data)

            if price:
                # Update order in database
                response = supabase.table('orders').update({"price": price}).eq("id", order_id).execute()
                assert len(response.data) > 0, "Error: Unable to update orders table with price"
                return jsonify({"price": price})
            else:
                message = "No profitable route options yet, order has been added to the database."
                return jsonify({message}) # this will need to be changed

        except Exception as e:
            return jsonify({"error": "Invalid input format or processing error"})
    else:
        return jsonify({"error": "Invalid request format (JSON expected)"})

# def midnight_eraser():
#     # erase supabase orders here

# schedule.every().day.at("00:00").do(midnight_eraser)

# def run_scheduler():
#     while True:
#         schedule.run_pending()



if __name__ == '__main__':
  app.run()

