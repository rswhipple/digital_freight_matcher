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
    home_base = (-84.3875298776525, 33.754413815792205)
    points = [home_base, order_data["pick_up"], order_data["drop_off"], home_base]
    new_route = {"points": points}

    response = supabase.table('routes').insert(new_route).execute()
    route_id = response.data[0]["id"]

    route_data = import_route(points)
    response = supabase.table('capacity').insert(new_route).execute()

    new_route.pickup = order_id.start
    new_route.dropoff = order_id.end
    # TODO update tables
    return new_route.id


def calculate_price(order_id):
    """calculates the price of a new order

    order_id: int -- order id to use for calculating price

    return: price as float
    """
    # query num of pallets in order
    # TODO where to get num pallets? 2 queries? contract_info + orders?
    #num_pallets = supabase.table('contract_info').select('Routes', 'Pallets') \    
        #.eq('Routes', ?which route?)execute()
    # "pallets" doesn't exist in 'orders' table yet
    num_pallets = supabase.table('orders').select('id', 'pallets') \
        .eq('id', order_id).execute()
    num_pallets = num_pallets.data[0]['pallets']

    # query pallet cost per mile
    pallet_cost_per_mile = supabase.table('costs') \
        .select('pallet_cost_per_mile').execute()
    pallet_cost_per_mile = pallet_cost_per_mile.data[0]['pallets']

    # query markup
    markup = supabase.table('costs').select('markup').execute()
    markup = markup.data[0]['markup']

    return num_pallets * pallet_cost_per_mile * (1 + markup)


def is_profitable(route_id):
    """checks to see if a new route is profitable

    route_id: int -- route id to check

    return: True if profitable, False otherwise
    """
    # query route distance
    total_miles = supabase.table('routes').select('id', 'total_miles') \
        .eq('id', route_id).execute()
    total_miles = total_miles.data[0]['total_miles']

    # query pallet cost per mile
    num_pallets = supabase.table('orders').select('id', 'pallets') \
        .eq('id', order_id).execute()
    num_pallets = num_pallets.data[0]['pallets']

    # query pallet cost per mile
    pallet_cost_per_mile = supabase.table('costs') \
        .select('pallet_cost_per_mile').execute()
    pallet_cost_per_mile = pallet_cost_per_mile.data[0]['pallets']

    # query markup
    markup = supabase.table('costs').select('markup').execute()
    markup = markup.data[0]['markup']

    OTC = total_miles * calc_total_costs()
    cargo_cost = num_pallets * pallet_cost_per_mile
    new_price = cargo_cost * (1 + markup)
    margin = (new_price - OTC) / OTC

    return margin > 0


def calc_total_costs():
    """Calculate total costs from spreadsheet

    Total = Trucker + Fuel + Leasing + Maintenance + Insurance

    return: total cost
    note: 'costs' table setup wrong direction
    """
    trucker = supabase.table('costs').select('trucker_cost').execute()
    trucker = trucker.data[0]['trucker']

    fuel = supabase.table('costs').select('fuel_cost').execute()
    fuel = fuel.data[0]['fuel']

    leasing = supabase.table('costs').select('leasing_cost').execute()
    leasing = leasing.data[0]['leasing']

    maintenance = supabase.table('costs').select('maintenance_cost').execute()
    maintenance = maintenance.data[0]['maintenance']

    insurance = supabase.table('costs').select('insurance_cost').execute()
    insurance = insurance.data[0]['insurance']

    return trucker + fuel + leasing + maintenance + insurance

