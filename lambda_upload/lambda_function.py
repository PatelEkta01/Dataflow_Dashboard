import boto3
import csv
import uuid
import os
import time  # ⏰ Add time module to store timestamps

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DDB_TABLE']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("✅ Received event:", event)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    filename = key.split('/')[-1]  # e.g., "data.csv"
    upload_time = int(time.time())  # 🕓 Add upload timestamp

    obj = s3.get_object(Bucket=bucket, Key=key)
    lines = obj['Body'].read().decode('utf-8').splitlines()
    reader = csv.DictReader(lines)

    if reader.fieldnames is None or None in reader.fieldnames:
        print("❌ Invalid CSV: missing or malformed headers.")
        return {"statusCode": 400, "body": "CSV file missing valid headers."}

    count = 0
    for row in reader:
        if not isinstance(row, dict) or None in row.keys():
            print("⚠️ Skipping malformed row:", row)
            continue

        row['record_id'] = str(uuid.uuid4())
        row['file_name'] = filename
        row['upload_time'] = upload_time  # 🆕 Add timestamp
        table.put_item(Item=row)
        count += 1

    return {
        "statusCode": 200,
        "body": f"✅ {count} rows from {filename} processed successfully."
    }
