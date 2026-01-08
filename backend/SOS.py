import json
import boto3
import os

# --- CONFIGURATION ---
# Initialize SNS Client targeting the SYDNEY region (ap-southeast-2)
# This is crucial because your ARN indicates the topic is hosted there.
sns = boto3.client('sns', region_name='ap-southeast-2')

def lambda_handler(event, context):
    # 1. DEBUGGING: Check what the Environment Variable actually holds
    env_arn = os.environ.get('SNS_TOPIC_ARN')
    print(f"DEBUG: Environment Variable Value: '{env_arn}'")

    # 2. HARDCODED ARN TEST
    # We use this directly to rule out any Environment Variable typos/spaces
    SNS_TOPIC_ARN = "arn:aws:sns:ap-southeast-1:844229254735:SOS"
    
    print(f"DEBUG: Using HARDCODED ARN: '{SNS_TOPIC_ARN}'")
    print(f"DEBUG: Incoming Event: {event}")

    try:
        # 3. Parse Data
        body = json.loads(event.get('body', '{}'))
        user_msg = body.get('message', 'NO_MESSAGE')
        location = body.get('location') 

        # 4. Format Email Content
        timestamp = context.aws_request_id
        
        if location and 'lat' in location and 'long' in location:
            lat = location['lat']
            long = location['long']
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{long}"
            
            email_content = (
                f"🚨 [EMERGENCY ALERT] - PRIORITY: HIGH\n"
                f"ID: {timestamp}\n"
                f"--------------------------------------------------\n"
                f"MESSAGE: {user_msg}\n"
                f"--------------------------------------------------\n"
                f"📍 GPS COORDINATES ACQUIRED:\n"
                f"LAT : {lat}\n"
                f"LONG: {long}\n\n"
                f"🔗 TACTICAL MAP VIEW:\n{google_maps_url}\n"
                f"--------------------------------------------------\n"
                f"SYSTEM: AWS Lambda / Portfolio Infrastructure"
            )
        else:
            email_content = (
                f"⚠️ [ALERT] - GPS SIGNAL LOST\n"
                f"ID: {timestamp}\n"
                f"MESSAGE: {user_msg}\n"
                f"LOCATION: Unknown\n"
            )

        # 5. Action: Publish to SNS
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=email_content,
            Subject=f"🚨 SOS SIGNAL DETECTED"
        )

        # 6. Success Response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'DISPATCHED',
                'sns_id': response['MessageId'],
                'note': 'Sent using HARDCODED ARN'
            })
        }

    except Exception as e:
        # Log the full error to CloudWatch
        print(f"CRITICAL FAILURE: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
