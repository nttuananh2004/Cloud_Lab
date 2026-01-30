# Last commit by TuanAnh dep trai
import json
import urllib.request
import boto3
import uuid
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# Table name configured via code or environment variable
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'NetProbeLogs')
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Network Diagnostics & Telemetry Handler.
    
    1. Extracts Caller IP and User-Agent from the request.
    2. Enriches data using a third-party Geolocation API.
    3. Persists the access log to DynamoDB for analytics.
    4. Returns network statistics to the frontend.
    """
    try:
        # 1. Request Context Extraction
        source_ip = "Unknown"
        user_agent = "Unknown"
        
        # Safely extract data from API Gateway v2 proxy integration
        if 'requestContext' in event and 'http' in event['requestContext']:
            http_info = event['requestContext']['http']
            source_ip = http_info.get('sourceIp', 'Unknown')
            user_agent = http_info.get('userAgent', 'Unknown')
        
        # 2. Geolocation Lookup (External API)
        # Note: Using free tier of ip-api.com
        url = f"http://ip-api.com/json/{source_ip}"
        geo_data = {}
        
        try:
            # Set User-Agent to avoid being blocked by the external API WAF
            req = urllib.request.Request(url, headers={'User-Agent': 'AWS-Lambda-Portfolio'})
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.getcode() == 200:
                    geo_data = json.loads(response.read().decode())
        except Exception as e:
            # Log warning but continue execution (Non-blocking failure)
            print(f"WARN: Geo API lookup failed: {e}")

        # 3. Data Preparation
        # Convert UTC to Local Time (Vietnam/ICT: UTC+7) for readability
        utc_now = datetime.utcnow()
        vn_time = utc_now + timedelta(hours=7)
        formatted_time = vn_time.strftime('%Y-%m-%d %H:%M:%S')

        # Construct the database record schema
        item = {
            'record_id': str(uuid.uuid4()),        # Partition Key
            'timestamp': formatted_time,           # Sort Key / Index
            'ip_address': source_ip,               
            'city': geo_data.get('city', 'Unknown'),
            'country': geo_data.get('country', 'Unknown'),
            'isp': geo_data.get('isp', 'Unknown'),
            'status': 'SUCCESS',
            'user_agent': user_agent
        }

        # 4. Persistence Layer (DynamoDB)
        try:
            table.put_item(Item=item)
            print(f"INFO: Record {item['record_id']} persisted to DynamoDB table {TABLE_NAME}.")
        except Exception as e:
            print(f"ERROR: Database Write Failed: {str(e)}")
            # Optimization: Do not return 500 to user if logging fails; return geo data only.

        # 5. Response Construction
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*', # Enable CORS
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps({
                'ip': source_ip,
                'city': item['city'],
                'country': item['country'],
                'isp': item['isp'],
                'lat': geo_data.get('lat', 0),
                'lon': geo_data.get('lon', 0)
            })
        }
    except Exception as e:
        # Catch-all for critical runtime errors
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}