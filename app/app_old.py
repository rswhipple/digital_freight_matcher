from flask import Flask, request, jsonify
from supabase import create_client, Client
import schedule
import time
import something
from pprint import pprint
from compare_routes import *

app = Flask(__name__)

supabase = create_client(something.url, something.something)


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
            pick_up = data.get("pick-up", {})   # make sure format is (lon, lat) ******************  this may cause error
            drop_off = data.get("drop-off", {})
            volume, weight, package_type = packages
            pickup = (pick_up.get("longitude", 0), pick_up.get("latitude", 0))
            dropoff = (drop_off.get("longitude", 0), drop_off.get("latitude", 0))

            print(f"pickup: {pickup}; dropoff: {dropoff}")

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
            print(e)
            return jsonify({"error": "Invalid input format or processing error"})
    else:
        return jsonify({"error": "Invalid request format (JSON expected)"})


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    # Check if the request contains JSON data
    if request.is_json:
        try:
            data = request.get_json()

            # Access specific data from the JSON input
            order_id = data.get("order_id", 0)

            # Add order to the routes table
            route_info = add_order_to_route(order_id)                  #*** tony's function, needs to return route_id and route_name ***

            # Update order status to confirmed
            response = supabase.table('orders').update("confirmed", True).eq("id", order_id).execute()

            message = f"Order has been confirmed and added to route {route_info['route_name']}, id {route_info['route_id']}."
            return message # this will need to be changed

        except Exception as e:
            return jsonify({"error": "Invalid input format or processing error"})
    else:
        return jsonify({"error": "Invalid request format (JSON expected)"})
    

def reset_databases():
    # erase all orders in 'orders' db    
    supabase.table('orders').delete().gte('id', 0)eq.execute()
    # add more tasks here if needed


def schedule_reset_at_midnight():
    # Schedule task to run daily at midnight
    schedule.every().day.at("00:00").do(reset_at_midnight)

    while True:
        # Run scheduled tasks
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # Run separate thread for scheduled resets
    from threading import Thread

    scheduler_thread = Thread(target=schedule_reset_at_midnight)
    scheduler_thread.start()

    # Run everything else aka the app
    app.run()

# def midnight_eraser():
#     # erase supabase orders here

# schedule.every().day.at("00:00").do(midnight_eraser)

# def run_scheduler():
#     while True:
#         schedule.run_pending()



#if __name__ == '__main__':
  #app.run()

