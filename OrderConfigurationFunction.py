# -*- coding: utf-8 -*-

import json
import uuid
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
order_table = dynamodb.Table('PizzaOrderTable')
menu_table = dynamodb.Table('PizzaOrder')

print "Loading functions.."


def lambda_handler(event, context):
    method = event['method']
    item = getMenuItems(event, context)
    print item

    if ((item != None) and method == "POST"):
        result = postOrder(event, context, item)
    elif (method == "PUT"):
        result = putSelection(event, context)
    elif (method == "GET"):
        result = getOrder(event, context)
    else:
        result = "Menu Not Found"
    return result


def getMenuItems(event, context):
    try:
        result = menu_table.get_item(
            Key={
                'menu_id': event['body']['menu_id']

            }
        )
        item = result['Item']
    except Exception as not_found:
        item = None
    return item


def postOrder(event, context, item):
    # table = dynamodb.Table('Order')
    menu_id = event['body']['menu_id']
    customer_name = event['body']['customer_name']
    customer_email = event['body']['customer_email']
    order_status = "selection"
    selection = item['selection']
    item = {
        'order_id': str(uuid.uuid1()),
        'menu_id': menu_id,
        'customer_name': customer_name,
        'customer_email': customer_email,
        'order_status': order_status
    }

    # write the menu items to the database
    order_table.put_item(Item=item)

    # create a response
    selection = dict(enumerate(selection, 1))
    response = {"Message": "Hi " + customer_name + ", please choose one of these selection: " + ' '.join(
        ['{}. {}'.format(k, v) for k, v in selection.iteritems()])}
    # response = { "Message": "Hi " + customer_name + ", please choose one of these selection: " + str(selection)}
    return response


def putSelection(event, context):
    order_id = event['params']['order-id']
    input = int(event['body']['input'])
    try:
        result = order_table.get_item(
            Key={
                'order_id': order_id

            }
        )
        order_status = result['Item']['order_status']
        menu_id = result['Item']['menu_id']
    except Exception as not_found:
        response = "Invalid Order Id"
        return response

    if order_status == "selection":
        result = menu_table.get_item(
            Key={
                'menu_id': menu_id

            }
        )
        selection = result['Item']['selection']
        size = result['Item']['size']
        price = result['Item']['price']
        selection = dict(enumerate(selection, 1))
        size = dict(enumerate(size, 1))
        price = dict(enumerate(price, 1))
        order = {}
        order['selection'] = selection.get(input)
        order['size'] = None
        # response = "In selection of base"

        result = order_table.update_item(
            Key={
                'order_id': order_id
            }, UpdateExpression="set order_status = :v1, #o = :v2",
            ExpressionAttributeNames={'#o': 'order'},
            ExpressionAttributeValues={
                ':v1': "size",
                ':v2': order
            },
            ReturnValues="UPDATED_NEW"
        )

        response = {
            "Message": "Which size do you want? " + ' '.join(['{}. {}'.format(k, v) for k, v in size.iteritems()])}
    elif order_status == "size":
        result = menu_table.get_item(
            Key={
                'menu_id': menu_id

            }
        )
        size = result['Item']['size']
        price = result['Item']['price']
        size = dict(enumerate(size, 1))
        price = dict(enumerate(price, 1))

        result = order_table.get_item(
            Key={
                'order_id': order_id

            }
        )
        # now = datetime.datetime.
        order = result['Item']['order']
        order_status = "processing"
        order['size'] = size.get(input)
        order['price'] = price.get(input)
        order['order_time'] = datetime.datetime.now().strftime('%Y-%m-%d@%H:%M:%S')
        result = order_table.update_item(
            Key={
                'order_id': order_id
            }, UpdateExpression="set order_status = :v1, #o = :v2",
            ExpressionAttributeNames={'#o': 'order'},
            ExpressionAttributeValues={
                ':v1': "processing",
                ':v2': order
            },
            ReturnValues="UPDATED_NEW"
        )
        response = {"Message": "Your order costs $" + order[
            'price'] + ". We will email you when the order is ready. Thank you!"}

    return response


def getOrder(event, context):
    order_id = event['params']['order-id']
    try:
        result = order_table.get_item(
            Key={
                'order_id': order_id

            }
        )
        response = result['Item']
    except Exception as not_found:
        response = "Invalid Order Id"
    return response