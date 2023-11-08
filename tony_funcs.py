# Tony's functions

# "new_order" function, handles a new order
    # receive order (json from form??)
    # create Order object and populate data from form
    # check if order is within range ("is_in_range" function?)
        # if True continue
        # if False return -1 
    # call "compare_routes"
    # if route_id is NULL
        # call "create_new_route"
        # call "is_profitable"
            # if True call "calculate_price" and return price
            # if False return 0
    # else if route_id is not NULL
        # assign route_id to OrderClass
        # call "add_order_to_route" with order_id of Order object
        # call "calculate_price" and return price
def new_order(order):
    """
    order: json from form?
    """
    new_order = Order(order)
    if (not is_in_range(new_order)):
        return -1

    route = compare_routes(new_order.id)
    if route.id == None:
        new_route = create_new_route(new_order.id)
        if is_profitable(new_route):
            return calculate_price(new_order.id)
        else:
            return 0
    else:
        new_order.route = route.id
        add_order_to_route(new_order.id)  # TODO check return value
        return calculate_price(new_order.id)


# "is_in_range" function, check if a new order is too far away
    # receives order_id 
    # calls "import_time" using points [Atlanta, pickup, drop_off, Atlanta]
    # if time > 10 hours
        # returns False
    # else returns True 
def is_in_range(order_id):
    return import_time(order_id) <= 10  # TODO what gets passed?; magic number


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
def create_new_route(order_id):
    new_route = Route(order_id)
    new_route.pickup = order_id.start
    new_route.dropoff = order_id.end
    import_route()  # TODO What gets passed?
    # TODO update tables
    return new_route.id


# "calculate_price" function, calculates the price of a new order
    # receives order_id
    # logic
    # returns price
def calculate_price(order_id):
    return (order_id.route.pallets + cargo) * PALLET_COST * (1 + MARKUP)


# "is_profitable" function, checks to see if a new route is profitable
    # receives route_id
    # logic
    # returns True or False
def is_profitable(route_id):
    OTC = route_id.distance * TOTAL_COSTS
    cargo_cost = PALLETS * PALLET_COST
    new_price = cargo_cost * (1 + MARKUP)
    margin = (new_price - OTC) / OTC
    return margin > 0
