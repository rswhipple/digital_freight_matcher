from supabase import create_client, Client

# "add_order_to_route" function, adds an order to a route
    # receives order_id (you can find route_id via order_id in database)
    # add pickup and drop_off points to routes table (in the correct order)
    # update route_geom and capacity in capacity_table (using Mapbox API)
    # update confirmed col in orders table 
    # update margins table
    # return EXIT_SUCCESS or EXIT_FAILURE
def add_order_to_route(order_id):  # TODO how to update table?
    pass


# "create_new_route" function, creates a new route
    # receives order_id 
    # create a new Route object
    # add pickup and drop_off points from the order, all points = [Atlanta, pickup, drop_off, Atlanta]
    # call "import_route" using new route_id and points
    # add RouteClass variable to routes table
    # assign route_id to order_id in orders table
    # update capacity table with route_geom (using Mapbox API)
    # update total_miles and total_time in routes table (using Mapbox API)
    # return route_id
#*** tony's function, needs to return route_id ***
            #response_data = {
            #    "volume": volume,
            #    "weight": weight,
            #    "package_type": package_type,
            #    "pick_up": pick_up,
            #    "drop_off": drop_off,
            #    "in_range": True,
            #}
# return value will go into is_profitable
def create_new_route(order_id, order_data):
    new_route = {
        "route_name": 
        "total_miles":
        "total_time":
        "points":
    }

    new_route.pickup = order_id.start
    new_route.dropoff = order_id.end
    import_route()  # TODO What gets passed?
    # TODO update tables
    return new_route.id


# "calculate_price" function, calculates the price of a new order
    # receives order_id
    # logic
    # returns price
    #price = calculate_price(order_id)                     #*** tony's function ***
def calculate_price(order_id):
    markup = supabase.table('margins').select('margin').execute()
    return (order_id.route.pallets + cargo) * PALLET_COST * (1 + MARKUP)


# "is_profitable" function, checks to see if a new route is profitable
    # receives route_id
    # logic
    # returns True or False
    #*** tony's function, if True returns all orders in route and their prices ***
def is_profitable(route_id):
    OTC = route_id.distance * TOTAL_COSTS
    cargo_cost = PALLETS * PALLET_COST
    new_price = cargo_cost * (1 + MARKUP)
    margin = (new_price - OTC) / OTC
    return margin > 0
