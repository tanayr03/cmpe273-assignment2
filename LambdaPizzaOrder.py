import json
import uuid
import boto3
import decimal


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('PizzaOrder')

print "Loading functions.."


def lambda_handler(event, context):
    method = event['method']
    response = None
    if (method == "POST"):
        response = postMenu(event, context)
    elif (method == "GET"):
        response = getMenu(event, context)
    elif (method == "PUT"):
        response = putMenu(event, context)
    elif (method == "DELETE"):
        response = delMenu(event, context)
    return response


def postMenu(event, context):
    store_name = event['body']['store_name']
    selection = event['body']['selection']
    size = event['body']['size']
    price = event['body']['price']
    store_hours = event['body']['store_hours']
    item = {
        'menu_id': str(uuid.uuid1()),
        'store_name': store_name,
        'selection': selection,
        'size': size,
        'sequence': ["selection", "size"],
        'price': price,
        'store_hours': store_hours
    }
    # write the menu items to the database
    table.put_item(Item=item)

    # create a response
    response = "200 Ok"
    return response


def getMenu(event, context):
    menu_id = event['params']['menu-id']
    result = table.get_item(
        Key={
            'menu_id': menu_id
        }
    )
    item = result['Item']
    return item


def putMenu(event, context):
    result = table.update_item(
        Key={
            'menu_id': event['params']['menu-id']
        }, UpdateExpression="set selection = :val",
        ExpressionAttributeValues={
            ':val': event['body']['selection']
        },
        ReturnValues="UPDATED_NEW"
    )

    # create a response
    response = "200 Ok"
    return response


def delMenu(event, context):
    menu_id = event['params']['menu-id']
    # pathParameters = event.get(pathParameters)
    # fetch todo from the database
    # menuId =  "cd8af4b8-36df-11e7-9e67-0a2f22f3a5b9"
    result = table.delete_item(
        Key={
            'menu_id': menu_id
        }
    )
    # create a response
    response = "200 Ok"

    return response