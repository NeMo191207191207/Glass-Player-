from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 's-maxage=60, stale-while-revalidate')
        self.end_headers()
        
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
            self.wfile.write(json.dumps(tracks).encode())
        else:
            self.wfile.write(b'[]')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.end_headers()
