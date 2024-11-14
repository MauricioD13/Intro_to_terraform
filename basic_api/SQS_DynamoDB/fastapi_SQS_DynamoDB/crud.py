import boto3
from pydantic import ValidationError
from schemas import RecipeCreate
from logger import logger
from aws import sqs, table
import asyncio
import os

async def create_recipe(recipe: RecipeCreate):
    try: 
        #recipe = MessageRecipe(**recipe_data)
        if hasattr(recipe, 'model_dump_json'):
            message_json = recipe.model_dump_json()
        else:
            logger.warning('Error with Pydantic version')
        response = sqs.send_message(
            QueueUrl = queue_url,
            MessageBody = message_json
        )
        return response['MessageId']
    except ValidationError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)

async def get_all_recipes():
    try:
        response = table.scan()
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        return items
    except Exception as e:
        logger.exception(f'Error in DynamoDB query: {e}')
        return None

async def get_recipe(attribute:  str, value: str):
    try:
        response = table.query(
            KeyConditionExpression=Key(attribute).eq(value)
        )
        return response['Items']
    except Exception as e:
        logger.exception(f'Error in DynamoDB query: {e}')