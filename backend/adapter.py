"""
AWS Lambda Local Adapter
Author: Tuan Anh (Cloud Architect)
Purpose: Facilitates local execution of serverless handlers within a containerized environment.
"""

import os
import json
import logging
import importlib
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for local frontend integration

# Configure structured logging for observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Adapter-Layer")

# Dynamic module loading based on environment configuration
MODULE_NAME = os.environ.get("MODULE_NAME", "sos")
PORT = int(os.environ.get("PORT", 8080))

try:
    # Dynamically import the specific Lambda handler module
    handler_module = importlib.import_module(MODULE_NAME)
    logger.info(f"Successfully initialized module: {MODULE_NAME}")
except ImportError as e:
    logger.error(f"Critical: Failed to import module {MODULE_NAME}. Error: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Service availability heartbeat."""
    return jsonify({
        "status": "HEALTHY",
        "service": MODULE_NAME,
        "environment": "local-container"
    }), 200

@app.route('/invoke', methods=['POST'])
def invoke_handler():
    """Simulates AWS Lambda execution environment."""
    try:
        # Construct the Lambda-proxy event structure
        event = {
            'body': request.get_data(as_text=True),
            'requestContext': {
                'http': {
                    'sourceIp': request.remote_addr,
                    'userAgent': request.headers.get('User-Agent')
                }
            }
        }
        
        # Mocking the AWS Context object
        context = type('obj', (object,), {'aws_request_id': 'local-execution-id'})
        
        # Execute business logic from the original handler
        response = handler_module.lambda_handler(event, context)
        
        # Parse and return the response compatible with API Gateway V2
        return jsonify(json.loads(response['body'])), response['statusCode']

    except Exception as e:
        logger.error(f"Handler Execution Failed: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Microservice starting on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)