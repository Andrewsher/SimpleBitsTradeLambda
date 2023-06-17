from Handler.BitsPriceHandler import BitsPriceHandler

def bits_price_lambda_handler(event, context):
    handler = BitsPriceHandler()
    res = handler.handle_request(event)
    print(res)
    return res
