from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB max

# Clé API depuis variable d'environnement Render
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/claude', methods=['POST'])
def claude_api():
    try:
        data = request.json
        messages = data.get('messages', [])
        system_prompt = data.get('system', '')
        
        if not messages:
            return jsonify({'error': 'Missing messages'}), 400
        
        if not ANTHROPIC_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500
        
        # Debug: log request info
        print(f"=== New API Request ===")
        print(f"System prompt: {len(system_prompt)} chars")
        print(f"Messages count: {len(messages)}")
        
        for i, msg in enumerate(messages):
            content = msg.get('content', '')
            if isinstance(content, list):
                types = [item.get('type') for item in content]
                print(f"  Message {i} ({msg.get('role')}): array with types {types}")
            else:
                print(f"  Message {i} ({msg.get('role')}): text ({len(content)} chars)")
        
        # Build API request
        api_request = {
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 2000,
            'messages': messages
        }
        
        # Add system prompt if provided
        if system_prompt:
            api_request['system'] = system_prompt
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01'
            },
            json=api_request
        )
        
        print(f"API response status: {response.status_code}")
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_text = response.text
            print(f"API error: {error_text}")
            return jsonify({
                'error': f'API Error: {response.status_code}',
                'details': error_text
            }), response.status_code
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
