from supabase import create_client, Client


def add_order_to_route(order_id):
    """adds an order to a given route

    order_id: int -- id of order to add to a route

    return: True if successful, False otherwise
    """
    # get route id
    route_id = supabase.table('orders').select('id', 'order_route_id') \
        .eq('id', order_id).execute()
    route_id = route_id[0]['order_route_id']

    # TODO add pickup and dropoff point to routes table
    # I'm assuming pickup and dropoff are from order and must be put in points
    # format
    
    # TODO update route_geom and capacity in 'capacity' (using Mapbox API)
    # is this same as create_new_route?

    # TODO update confirmed col in orders table 
    # confirm_order()?

    # TODO update margins table

    return True


def create_new_route(order_id, order_data):
    """creates a new route in database

    order_id: int -- order id for needing new route
    order_data: dict -- data of order for new route

    return: id of new route created
    """
    # build new route
    home_base = (-84.3875298776525, 33.754413815792205)
    points = [home_base, order_data["pick_up"], order_data["drop_off"], home_base]
    new_route = {"points": points}

    # insert into 'routes' table
    route_id = supabase.table('routes').insert(new_route).execute()
    route_id = route_id.data[0]["id"]

    # calculate data
    route_data = import_route(points)

    # insert into 'capacity' table
    response = supabase.table('capacity').insert(route_data).execute()

    return route_id


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

