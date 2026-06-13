from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ─── NewsAPI key is read from Vercel Environment Variable ───────────────────
# It is NEVER hardcoded here. Safe to push on GitHub.
API_KEY = os.environ.get('NEWS_API_KEY', '')
BASE_URL = 'https://newsapi.org/v2'


@app.route('/api/news', methods=['GET'])
def get_news():
    """
    Fetch top headlines by category.
    Query param: ?category=technology  (default: general)
    """
    if not API_KEY:
        return jsonify({'error': 'NEWS_API_KEY environment variable not set.'}), 500

    category = request.args.get('category', 'general')
    allowed  = {'general','technology','business','science','health','sports','entertainment'}

    if category not in allowed:
        return jsonify({'error': 'Invalid category'}), 400

    try:
        response = requests.get(
            f'{BASE_URL}/top-headlines',
            params={
                'category': category,
                'language': 'en',
                'pageSize': 24,
                'apiKey':   API_KEY,
            },
            timeout=10
        )
        data = response.json()

        if data.get('status') != 'ok':
            return jsonify({'error': data.get('message', 'NewsAPI error')}), 502

        # Parse JSON response — filter out removed articles
        articles = [
            {
                'title':       a.get('title', ''),
                'description': a.get('description', ''),
                'url':         a.get('url', ''),
                'urlToImage':  a.get('urlToImage', ''),
                'publishedAt': a.get('publishedAt', ''),
                'source':      a.get('source', {}).get('name', 'Unknown'),
            }
            for a in data.get('articles', [])
            if a.get('title') and a.get('title') != '[Removed]'
        ]

        return jsonify({'status': 'ok', 'totalResults': len(articles), 'articles': articles})

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request to NewsAPI timed out.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 502


@app.route('/api/search', methods=['GET'])
def search_news():
    """
    Search news by keyword.
    Query param: ?q=bitcoin
    """
    if not API_KEY:
        return jsonify({'error': 'NEWS_API_KEY environment variable not set.'}), 500

    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter q is required.'}), 400

    try:
        response = requests.get(
            f'{BASE_URL}/everything',
            params={
                'q':        query,
                'language': 'en',
                'sortBy':   'publishedAt',
                'pageSize': 24,
                'apiKey':   API_KEY,
            },
            timeout=10
        )
        data = response.json()

        if data.get('status') != 'ok':
            return jsonify({'error': data.get('message', 'NewsAPI error')}), 502

        # Parse JSON response
        articles = [
            {
                'title':       a.get('title', ''),
                'description': a.get('description', ''),
                'url':         a.get('url', ''),
                'urlToImage':  a.get('urlToImage', ''),
                'publishedAt': a.get('publishedAt', ''),
                'source':      a.get('source', {}).get('name', 'Unknown'),
            }
            for a in data.get('articles', [])
            if a.get('title') and a.get('title') != '[Removed]'
        ]

        return jsonify({'status': 'ok', 'totalResults': len(articles), 'articles': articles})

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 502


# Local development server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
