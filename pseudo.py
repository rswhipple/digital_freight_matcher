# TASKS 2023-11-04
Alan - #1 Create database with 7 tables listed above
Prakash - #2 Create all the classes
Becky - #3 Create functions: "import_route", "empty_capacity", "compare_routes", "check_points", "check_capacity", "check_time"
Tony - #4 Create functions: "new_order", "add_order_to_route", "create_new_route", "calculate_price", "is_profitable"


""" Description: Pseudo code for the Digital Freight project """

""" database """
# create database with tables [routes, capacity, truck_info, orders, costs, cargo, margins] (see below)
# each table should be a class (?)
    
""" routes class / table """
# create routes table with cols [route_id, points, total_miles, total_time]
    # route_id is assigned in database
    # points(lon, lat), only the pickup/ drop_off points taken from assignement 
    # total_miles is imported from Mapbox API
    # total_time is imported from Mapbox API

""" capacity class / table """
# create capacity table with cols [route_id, route_geom(coordinates), empty_vol, empty_weight]
    # route_id references routes table
    # route_geom is imported from Mapbox API
    # empty_vol defaults to 1700 (cubic feet)
    # empty_weight defaults to 9180 (pounds)

""" truck_info class / table """
# create truck info table with cols ( truck_id, route_id, route_geom(coordinates), capacity_vol, capacity_weight )
    # truck_id assigned in database (?)
    # route_id references routes table (we only have 1 type of truck now, but I've included this if the client has different size trucks in the future)
    # capacity_vol capacity defaults to 1700 (cubic feet)
    # capacity_weight capacity defaults to 9180 (pounds)
    # pallet_cost (per mile) is calculated from costs and cargo tables:   total_cost / (capacity_vol / 64)
    # std_package_cost (per mile) is calculated from costs and cargo tables:   total_cost / (capacity_vol / 18)

""" order class / table """
# create orders table with cols [order_id, route_id, pickup, drop_off, cargo, price, confirmed]
    # order_id is assigned in database or from order form
    # pickup point(long, lat) is taken from order form
    # drop_off point(long, lat) is taken from order form
    # cargo_type is taken from order form (pallet or std_package)
    # total_vol is taken from order form (num_packages * cargo_vol of type)
    # total_weight is taken from order form (num_packages * cargo_weight of type)
    # route_id references routes table, "n/a" if order is not yet assigned to a route
    # price is calculated using Tony's logic ...
    # confirmed is True or False, defaults to False

""" costs class / table """
# create costs table with cols [total_cost, trucker, fuel, leasing, maintenance, insurance, miles_gallon, gas_price]
    # total_cost (per mile) is the sum of trucker, fuel, leasing, maintenance, insurance
    # fuel is gas_price / miles_gallon

""" cargo class / table """
# create cargo table with cols [cargo_type, cargo_vol, cargo_cost]
    # cargo_type is pallet or std_package
    # cargo_vol is taken from spreadsheets, pallet = 64 cubic feet, std_package = 18 cubic feet

""" margins class / table """
# create margins table with cols ( route_id, operational_cost, income, margin )
    # route_id references routes table
    # operational_cost is total_miles * total_cost
    # income is calculated from orders table
    # margin is calculated from operational_cost and income



""" functions """
# "import_route" function, imports route_geom from Mapbox API
    # receives a dynamic number of points (minimum 2), and route_id (if available)
    # create access_token variable
    # convert points into MapBox API request url
    # make the API request
    # check if the request was successful (HTTP status code 200)
    # if successful, parse into route_geom
    # return route_geom (total_time, total_miles, coordinates)

# "empty_capacity" function, calculates empty_capacity from orders table
    # route_id
    # query orders table for orders with route_id
    # empty_capacity is route_id -> truck_id -> (capacity_vol - sum of total_vol of orders) 
        # but this is more complex, because we need to check when cargo is picked up and dropped off
    # return empty_capacity

# "new_order" function, handles a new order
    # receive order (from form??)
    # create temp OrderClass variable
    # call "compare_routes"
    # if route_id is NULL, call "create_new_route"
    # if route_id is not NULL, call "add_order_to_route"

# "compare_routes" function, checks order against existing routes, receives order_id
    # for each order
        # create temp RouteClass variable set to NULL ? not sure how to handle temporary routes
        # call "check_points"
        # if temp RouteClass variable != NULL 
            # create temp CapacityClass variable set to NULL
            # call "check_capacity" 
                # if True call "check_time"
                    # if True set route_id to temp_route_id
                    # else break
                # else break
        # else break
    # return temp RouteClass variable

# "check_points" function, checks if a route is within 1 km of an order, recieves temp RouteClass variable, order_id
    # use POSTGIS to check if pick up is within 1 km of route
    # use POSTGIS to check if drop off is within 1 km of route && after pick up
    # if both are True, 
        # temp RouteClass variable = route_id
        # points = original points + order.pickup + order.drop_off (in the correct order)
    # return temp RouteClass variable

# "check_capacity" function, checks if route has empty_capacity for order, receives route_id, order_id
    # check if empty_vol is greater than order.total_vol between pickup and drop_off
    # check if empty_weight is greater than order.total_weight between pickup and drop_off
    # return True if both are True, else return False

# "check_time" function, checks if new route time exceeds 10 hours, receives route_id, order_id
    # check if new route time is less than 10 hours 
    # return True if True, else return False

# "add_order_to_route" function, adds an order to a route
    # add pickup and drop_off points to routes table (in the correct order)
    # update route_geom in coordinates table (using Mapbox API)
    # update confirmed col in orders table 
    # update margins table

# "create_new_route" function, creates a new route
    # create an empty route in routes table
    # add pickup and drop_off points to routes table (in the correct order)
    # update capacity table with route_geom (using Mapbox API)
    # update total_miles and total_time in routes table (using Mapbox API)

# "calculate_price" function, calculates the price of a new order

# "is_profitable" function, checks to see if a new route is profitable
