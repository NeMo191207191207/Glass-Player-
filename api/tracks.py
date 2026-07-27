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
    
    # Try multiple paths for tracks.json
    tracks = None
    possible_paths = [
        os.path.join(os.getcwd(), 'tracks.json'),
        os.path.join(os.path.dirname(__file__), '..', 'tracks.json'),
        '/var/task/tracks.json',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                tracks = json.load(f)
            break
    
    if tracks:
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
