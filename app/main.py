# app/connect.py
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_table():
    return boto3.resource("dynamodb", region_name="us-east-1").Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    """
    Handle new WebSocket connection: store connection ID (and user info) in DynamoDB.
    Requires a valid authorizer context to proceed.
    """
    connection_id = event["requestContext"]["connection_id"]

    authorizer_context = event["requestContext"].get("authorizer")
    if not authorizer_context:
        logger.error("Unauthorized: no authorizer provided.")
        return {"statusCode": 403, "body": "Unauthorized"}

    user_id = authorizer_context.get("principalId")
    item = {"connection_id": connection_id}
    if user_id:
        item["userId"] = user_id

    table = get_table()
    try:
        table.put_item(Item=item)
        logger.info(f"Connected: stored connection {connection_id}" + (f" for user {user_id}" if user_id else ""))
    except Exception as e:
        logger.error(f"Error storing connection_id {connection_id} in DynamoDB: {e}")
        return {"statusCode": 500, "body": "Failed to connect."}

    return {"statusCode": 200, "body": "Connected."}