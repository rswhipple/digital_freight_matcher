MAX_PALLETS = 26.6
PALLET_COST = 0.06376832579
MARKUP = 0.5

def pricing(route, cargo, data)
    """
    TODO: agree on data & function interfaces
    """
    # does it fit on truck?
    if route["pallets"] + cargo <= MAX_PALLETS:
        # calculate price
        # (current pallets + new pallets) * pallet cost * markup
        return (route["pallets"] + cargo) * PALLET_COST * (1 + MARKUP)
        # alternative: calculate price of only NEW cargo
        # new pallets * pallet cost * markup
        # return cargo * PALLET_COST * (1 + MARKUP)
    else:  # cargo does not fit on truck, make own route
        # TODO: make new route
        # calculate total distance in miles including ride back
        # multiply Total Costs (per mile) by total miles for Operational Truck Cost
        # multiply number of pallets by Pallet Cost/mile for Cargo Cost
        # Price (Based on cargo cost) = Cargo Cost * (1 + Markup)
        # Margin = (Price - OTC) / OTC
        # if Margin > 0:
            # route is profitable; return price
        # else:
            # route is not profitable; return None

