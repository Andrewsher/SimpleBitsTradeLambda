from Handler.BitsPriceHandler import BitsPriceHandler

def bits_price_lambda_handler(event, context):
    print(event)
    print(context)

    handler = BitsPriceHandler()
    handler.handle_request(event)
    print(event)
    return event
