import json
import os

def handler(request):
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
            },
        }
    
    tracks_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tracks.json')
    
    if os.path.exists(tracks_path):
        with open(tracks_path, 'r', encoding='utf-8') as f:
            tracks = json.load(f)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 's-maxage=60, stale-while-revalidate',
            },
            'body': json.dumps(tracks),
        }
    else:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': '[]',
        }
