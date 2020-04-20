import os
import boto3
import decimal
import json
from boto3.dynamodb.conditions import Key, Attr

import env_vars
ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', 'No value set')
SECRET_KEY = os.environ.get('S3_SECRET_KEY', 'No value set')

## Ref: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.04.html
## Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def query(thing_names, latest_ts=0):
    # For conditions see: https://boto3.amazonaws.com/v1/documentation/api/latest/_modules/boto3/dynamodb/conditions.html
    client = boto3.client('dynamodb', aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('iot_table')

    results = []
    for thing in thing_names:
        response = table.query(
            KeyConditionExpression=Key('deviceId').eq(thing) & Key('timestamp').gt(str(latest_ts))
        )
        response = json.loads(json.dumps(response, indent=4, cls=DecimalEncoder))
        results = results + response.get('Items')
    return results