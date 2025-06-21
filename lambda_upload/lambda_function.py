import boto3
import csv
import uuid
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DDB_TABLE']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Received event:", event)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    obj = s3.get_object(Bucket=bucket, Key=key)
    lines = obj['Body'].read().decode('utf-8').splitlines()
    reader = csv.DictReader(lines)

    for row in reader:
        row['record_id'] = str(uuid.uuid4())
        table.put_item(Item=row)

    return {"statusCode": 200, "body": "Data processed."}
