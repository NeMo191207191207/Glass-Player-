import json
import time
from yandex_music import Client

TOKEN_CACHE = {}

def handler(request):
    # Handle CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
        }
    
    # Get query parameters
    query = request.query or {}
    track_id = query.get('trackId')
    token = query.get('token')
    
    if not track_id or not token:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'trackId and token required'}),
        }
    
    # Check cache
    if track_id in TOKEN_CACHE:
        cached = TOKEN_CACHE[track_id]
        if time.time() - cached['time'] < 1800:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'url': cached['url']}),
            }
    
    try:
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
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'url': url}),
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'No download info'}),
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
        }
