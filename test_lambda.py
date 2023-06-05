from Handler.BitsPriceHandler import BitsPriceHandler

def lambda_handler(event, context):
    print(event)
    print(context)

    handler = BitsPriceHandler(event["user"])
    handler.handle_request(event)
    print(event)
    return event
