# Last commit by TuanAnh dep trai
import json
import boto3
import os

# --- INFRASTRUCTURE CONFIGURATION ---
# Dynamically determine the region from the execution environment to ensure portability.
# Defaulting to 'ap-southeast-1' (Singapore) if not specified.
REGION = os.environ.get('AWS_REGION', 'ap-southeast-1')
sns = boto3.client('sns', region_name=REGION)

def lambda_handler(event, context):
    """
    Emergency Broadcast Handler.
    
    Triggered by: API Gateway (POST request).
    Action: Parses GPS coordinates and broadcasts a high-priority alert via AWS SNS.
    """
    try:
        # 1. Security Configuration Check
        # Retrieve the SNS Topic ARN from Environment Variables.
        # This prevents sensitive Account IDs from being exposed in the source code.
        SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
        
        if not SNS_TOPIC_ARN:
            print("CRITICAL ERROR: 'SNS_TOPIC_ARN' is missing in environment variables.")
            raise ValueError("Server Configuration Error: Missing SNS Topic ARN.")

        # 2. Payload Parsing & Validation
        print(f"INFO: Processing SOS Signal. Request ID: {context.aws_request_id}")
        
        # Handle body parsing whether it comes as a string or dict
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
            
        user_msg = body.get('message', 'NO_MESSAGE')
        location = body.get('location') 

        # 3. Content Formatting
        # Construct a deep-link for Google Maps if valid coordinates are provided.
        timestamp = context.aws_request_id
        map_link = "Location Data Unavailable"
        gps_info = "GPS SIGNAL LOST"
        
        if location and 'lat' in location and 'long' in location:
            lat = location['lat']
            long = location['long']
            # Generate universal Google Maps link
            map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{long}"
            gps_info = f"LAT: {lat}\nLONG: {long}"
            
        # Construct the emergency message payload
        email_content = (
            f"🚨 [EMERGENCY ALERT] - PRIORITY: HIGH\n"
            f"ID: {timestamp}\n"
            f"MESSAGE: {user_msg}\n"
            f"--------------------------------------------------\n"
            f"📍 TELEMETRY DATA:\n{gps_info}\n\n"
            f"🔗 TACTICAL MAP:\n{map_link}\n"
            f"--------------------------------------------------\n"
            f"SYSTEM: AWS Lambda / Portfolio Infrastructure"
        )

        # 4. Broadcast Execution
        # Publish message to the SNS Topic (Fans out to Email/SMS subscribers)
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=email_content,
            Subject="🚨 SOS SIGNAL DETECTED"
        )

        # 5. Success Response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', # CORS Support
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'DISPATCHED',
                'sns_id': response['MessageId'],
                'timestamp': timestamp
            })
        }

    except Exception as e:
        # Log the full error to CloudWatch for debugging
        print(f"ERROR: SOS Execution Failed: {str(e)}")
        
        # Return a generic error to the client to avoid leaking internal stack traces
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal Server Error'})
        }