import json
import boto3
import base64

# Initialize Clients
rekognition = boto3.client('rekognition', region_name='ap-southeast-1')
bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-southeast-1')

def lambda_handler(event, context):
    try:
        print("Received event:", event)
        
        # 1. Parse Input
        # FIX: Phải dùng json.loads(event['body']) vì API Gateway gửi body dạng string
        if 'body' not in event or not event['body']:
             raise ValueError("No body found in request")
             
        body = json.loads(event['body'])
        
        # FIX: Đổi key thành 'source' và 'target' cho khớp với HTML
        img1_b64 = body.get('source', '').split(',')[-1]
        img2_b64 = body.get('target', '').split(',')[-1]

        if not img1_b64 or not img2_b64:
            raise ValueError("Images are missing")

        # Decode to binary
        img1_bytes = base64.b64decode(img1_b64)
        img2_bytes = base64.b64decode(img2_b64)

        # 2. Rekognition (Security Check)
        rek_response = rekognition.compare_faces(
            SourceImage={'Bytes': img1_bytes},
            TargetImage={'Bytes': img2_bytes},
            SimilarityThreshold=0
        )
        
        matches = rek_response['FaceMatches']
        similarity_score = 0.0
        if matches:
            similarity_score = matches[0]['Similarity']
            
        # FIX: Tạo biến matched để HTML hiện đúng/sai
        is_matched = similarity_score > 80  # Ngưỡng giống nhau > 80%

        # 3. Bedrock (AI Analysis - Claude 3 Haiku)
        en_text = "Analysis skipped."
        vn_text = "Analysis skipped."
        
        # Chỉ gọi AI nếu ảnh có nét tương đồng (để tiết kiệm tiền) hoặc ông muốn gọi luôn cũng được
        if similarity_score > 10: 
            prompt = f"""
            You are a biometric security expert.
            Task: Analyze the person in the first image. Describe facial features (eyes, nose, skin) and expression.
            Context: These two images have a similarity score of {similarity_score:.1f}%.
            
            OUTPUT FORMAT (Strict JSON only, no markdown):
            {{
                "en": "Write 1 short sentence in English analyzing the face.",
                "vn": "Dịch câu đó sang tiếng Việt, giọng văn chuyên nghiệp."
            }}
            """

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
                
                # Parse AI JSON
                start_json = ai_text.find('{')
                end_json = ai_text.rfind('}') + 1
                if start_json != -1 and end_json != -1:
                    ai_data = json.loads(ai_text[start_json:end_json])
                    en_text = ai_data.get("en", ai_text)
                    vn_text = ai_data.get("vn", "Translation unavailable")
                else:
                    en_text = ai_text
            except Exception as e:
                print(f"Bedrock Error: {str(e)}")
                # Không crash app nếu AI lỗi, chỉ log lại
                pass

        # 4. Return Response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', # Quan trọng: CORS
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'matched': is_matched,         # Cái này quan trọng cho HTML
                'similarity': round(similarity_score, 2),
                'analysis_en': en_text,
                'analysis_vn': vn_text
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({'error': str(e)})
        }
