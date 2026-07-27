import json
import time
import urllib.parse
import os

# Try to import yandex_music, handle if not available
try:
    from yandex_music import Client
    YM_AVAILABLE = True
except ImportError:
    YM_AVAILABLE = False

TOKEN_CACHE = {}

def handler(request):
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return {
            'status': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    # Get query params
    url = urllib.parse.urlparse(request.url if hasattr(request, 'url') else '')
    params = urllib.parse.parse_qs(url.query)
    
    track_id = params.get('trackId', [None])[0]
    token = params.get('token', [None])[0]
    
    if not track_id or not token:
        return {
            'status': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'trackId and token required'})
        }
    
    if not YM_AVAILABLE:
        return {
            'status': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'yandex-music not installed'})
        }
    
    # Check cache
    if track_id in TOKEN_CACHE:
        cached = TOKEN_CACHE[track_id]
        if time.time() - cached['time'] < 1800:
            return {
                'status': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'url': cached['url']})
            }
    
    try:
        token = urllib.parse.unquote(token)
        client = Client(token).init()
        
        parts = track_id.split(':')
        track = client.tracks([f'{parts[0]}:{parts[1]}'])[0]
        info = track.get_download_info()
        
        url = None
        for d in info:
            if d.codec == 'mp3':
                url = d.get_direct_link()
                break
        if not url and info:
            url = info[0].get_direct_link()
        
        if url:
            TOKEN_CACHE[track_id] = {'url': url, 'time': time.time()}
            return {
                'status': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'url': url})
            }
        else:
            return {
                'status': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'No download info'})
            }
    except Exception as e:
        return {
            'status': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
