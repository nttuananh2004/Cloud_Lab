import json
import urllib.request

def lambda_handler(event, context):
    try:
        # 1. Retrieve the user's IP address from the request event
        source_ip = "Unknown"
        if 'requestContext' in event and 'http' in event['requestContext']:
            source_ip = event['requestContext']['http']['sourceIp']
        
        # 2. Call free external API to fetch geolocation data based on the IP
        url = f"http://ip-api.com/json/{source_ip}"
        geo_data = {}
        
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.getcode() == 200:
                    geo_data = json.loads(response.read().decode())
        except:
            pass # Ignore errors, fall back to unknown values

        # 3. Return the JSON response with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # IMPORTANT: Enable CORS to allow access from the web frontend
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps({
                'ip': source_ip,
                'city': geo_data.get('city', 'Unknown'),
                'country': geo_data.get('country', 'Unknown'),
                'isp': geo_data.get('isp', 'Unknown'),
                'lat': geo_data.get('lat', 0),
                'lon': geo_data.get('lon', 0)
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}