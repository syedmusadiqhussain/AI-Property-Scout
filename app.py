from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import requests

load_dotenv('property-scout-server/.env')

app = Flask(__name__)

SERPER_API_KEY = os.getenv('SERPER_API_KEY')
BROWSERLESS_API_KEY = os.getenv('BROWSERLESS_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_properties():
    data = request.json
    query = data.get('query', '10 Marla house DHA Phase 6 under 5 Crore')

    try:
        response = requests.post(
            'https://google.serper.dev/search',
            json={
                'q': query,
                'num': 10,
            },
            headers={
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json',
            },
        )
        response.raise_for_status()
        search_results = response.json()

        # Extract URLs from organic results
        urls = []
        if 'organic' in search_results:
            for result in search_results['organic'][:5]:  # Take first 5
                if 'link' in result:
                    urls.append(result['link'])

        return jsonify({'search_results': search_results, 'urls': urls})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/extract', methods=['POST'])
def extract_property_data():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL required'}), 400

    try:
        response = requests.post(
            f'https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}',
            json={'url': url},
            headers={
                'Content-Type': 'application/json',
            },
        )
        response.raise_for_status()

        return jsonify({'content': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_properties():
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'Text required'}), 400

    try:
        response = requests.post(
            'https://router.huggingface.co/hf-inference/models/distilbert-base-uncased-finetuned-sst-2-english',
            json={
                'inputs': text,
            },
            headers={
                'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
                'Content-Type': 'application/json',
            },
        )
        response.raise_for_status()

        return jsonify({'analysis': response.json()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/find_house', methods=['GET'])
def find_house():
    # Full cycle: Search -> Extract -> Analyze
    query = '10 Marla house DHA Phase 6 under 5 Crore'

    # Step 1: Search
    search_response = requests.post(
        'https://google.serper.dev/search',
        json={
            'q': query,
            'num': 10,
        },
        headers={
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json',
        },
    )
    search_data = search_response.json()

    urls = []
    if 'organic' in search_data:
        for result in search_data['organic'][:3]:  # Take first 3
            if 'link' in result:
                urls.append(result['link'])

    results = []
    for url in urls:
        # Step 2: Extract
        extract_response = requests.post(
            f'https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}',
            json={'url': url},
            headers={
                'Content-Type': 'application/json',
            },
        )
        content = extract_response.text

        # Step 3: Analyze
        analyze_response = requests.post(
            'https://router.huggingface.co/hf-inference/models/distilbert-base-uncased-finetuned-sst-2-english',
            json={
                'inputs': content[:512],  # Limit text length
            },
            headers={
                'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
                'Content-Type': 'application/json',
            },
        )
        analysis = analyze_response.json()

        results.append({
            'url': url,
            'content': content,
            'analysis': analysis
        })

    return jsonify({
        'query': query,
        'search_results': search_data,
        'extracted_data': results
    })

if __name__ == '__main__':
    app.run(debug=True)
