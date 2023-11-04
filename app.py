from flask import Flask, request, jsonify
from supabase import create_client, Client
import something
from pprint import pprint

app = Flask(__name__)

supabase = create_client(something.url, something.something)

# Function to Fetch All Orders
def find_all_orders():
    data = supabase.table('orders').select("*").execute()
    # Equivalent for SQL Query "SELECT * FROM Orders;"
    return data.data


@app.route('/')
def index():
    orders = find_all_orders()
  
    # print to console
    pprint(orders)
    # print to frontend
    return f'{orders}'


@app.route('/receive_order', methods=['POST'])
def process_order():
    # Check if the request contains JSON data
    if request.is_json:
        try:
            data = request.get_json()

            # Access specific data from the JSON input
            cargo = data.get("cargo", {})
            packages = cargo.get("packages", [])
            pick_up = data.get("pick-up", {})
            drop_off = data.get("drop-off", {})

            cbm, weight, package_type = packages
            latitude_pick_up = pick_up.get("latitude", 0)
            longitude_pick_up = pick_up.get("longitude", 0)
            latitude_drop_off = drop_off.get("latitude", 0)
            longitude_drop_off = drop_off.get("longitude", 0)

            # Process the data or return a response as needed
            response_data = {
                "message": "Data received and processed successfully",
                "cbm": cbm,
                "weight": weight,
                "package_type": package_type,
                "latitude_pick_up": latitude_pick_up,
                "longitude_pick_up": longitude_pick_up,
                "latitude_drop_off": latitude_drop_off,
                "longitude_drop_off": longitude_drop_off,
            }

            return jsonify(response_data)

        except Exception as e:
            return jsonify({"error": "Invalid input format or processing error"})
    else:
        return jsonify({"error": "Invalid request format (JSON expected)"})


if __name__ == '__main__':
  app.run()
