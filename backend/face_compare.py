# Last commit by TuanAnh dep trai
import json
import boto3
import base64

# --- AI CLIENT INITIALIZATION ---
# Initializing clients outside handler for connection reuse (Warm Start)
rekognition = boto3.client('rekognition', region_name='ap-southeast-1')
bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-southeast-1')

def lambda_handler(event, context):
    """
    Biometric Analysis Handler.
    
    Workflow:
    1. Validates and decodes Base64 image inputs.
    2. Compares faces using Amazon Rekognition.
    3. If similarity > 10%, invokes Amazon Bedrock (Claude 3 Haiku) for a natural language summary.
    """
    try:
        print("INFO: Processing Face Comparison Request")
        
        # 1. Input Validation & Parsing
        if 'body' not in event or not event['body']:
             raise ValueError("Empty request body")
             
        body = json.loads(event['body'])
        
        # Extract base64 image strings (removing data:image/jpeg;base64 header if present)
        img1_b64 = body.get('source', '').split(',')[-1]
        img2_b64 = body.get('target', '').split(',')[-1]

        if not img1_b64 or not img2_b64:
            raise ValueError("Missing source or target image data.")

        # Decode to binary bytes for AWS SDK
        img1_bytes = base64.b64decode(img1_b64)
        img2_bytes = base64.b64decode(img2_b64)

        # 2. Facial Comparison (Computer Vision)
        # SimilarityThreshold=0 ensures we get a score even for low matches
        rek_response = rekognition.compare_faces(
            SourceImage={'Bytes': img1_bytes},
            TargetImage={'Bytes': img2_bytes},
            SimilarityThreshold=0
        )
        
        matches = rek_response['FaceMatches']
        similarity_score = 0.0
        if matches:
            similarity_score = matches[0]['Similarity']
            
        # Determine match status (Threshold set to 80% confidence)
        is_matched = similarity_score > 80

        # 3. GenAI Analysis (LLM Integration)
        en_text = "Analysis skipped (Low similarity confidence)."
        vn_text = "Analysis skipped."
        
        # Cost Optimization: Only invoke expensive LLM if images are somewhat similar (>10%)
        if similarity_score > 10: 
            prompt = f"""
            Role: Biometric Security Expert.
            Task: Analyze the person in the first image. Briefly describe facial features (eyes, nose, skin) and expression.
            Context: The comparison returned a similarity score of {similarity_score:.1f}%.
            
            OUTPUT FORMAT (Strict JSON only, no markdown):
            {{
                "en": "One sentence summary in English.",
                "vn": "Vietnamese translation of the summary."
            }}
            """

            # Payload for Claude 3 Haiku
            bedrock_body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            { "type": "image", "source": { "type": "base64", "media_type": "image/jpeg", "data": img1_b64 } },
                            { "type": "text", "text": prompt }
                        ]
                    }
                ]
            })

            try:
                bed_response = bedrock.invoke_model(
                    modelId='anthropic.claude-3-haiku-20240307-v1:0',
                    body=bedrock_body
                )
                
                result_json = json.loads(bed_response['body'].read())
                ai_text = result_json['content'][0]['text']
                
                # Extract JSON from LLM response (Defensive parsing)
                start_json = ai_text.find('{')
                end_json = ai_text.rfind('}') + 1
                if start_json != -1 and end_json != -1:
                    ai_data = json.loads(ai_text[start_json:end_json])
                    en_text = ai_data.get("en", ai_text)
                    vn_text = ai_data.get("vn", "Translation unavailable")
                else:
                    en_text = ai_text
            except Exception as e:
                print(f"WARN: Bedrock/LLM Generation failed: {str(e)}")
                # Fail gracefully: Return comparison result without AI analysis

        # 4. Final Response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', # CORS
                'Content-Type': 'application/json',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'matched': is_matched,
                'similarity': round(similarity_score, 2),
                'analysis_en': en_text,
                'analysis_vn': vn_text
            })
        }

    except Exception as e:
        print(f"ERROR: Runtime Exception: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal Server Error'})
        }