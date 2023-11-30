# query from order info from orders table

#   order_table = "orders" 

#   query = f"""
#     SELECT pickup, drop_off, order_vol, order_weight
#     FROM {order_table}
#     WHERE id = {order_id};
#     """
  
#   # Execute the query
#   response = supabase.query(query)

#   if response.status_code == 200:
#     order = response.get("data")
#     pickup = order[0]["pickup"]
#     drop_off = order[0]["drop_off"]