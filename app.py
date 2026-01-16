from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Clé API depuis variable d'environnement Render
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/claude', methods=['POST'])
def claude_api():
    try:
        data = request.json
        messages = data.get('messages')
        
        if not messages:
            return jsonify({'error': 'Missing messages'}), 400
        
        if not ANTHROPIC_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 1500,
                'messages': messages
            }
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': f'API Error: {response.status_code}',
                'details': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
