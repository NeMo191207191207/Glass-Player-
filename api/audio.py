from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import time

TOKEN_CACHE = {}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        track_id = params.get('trackId', [None])[0]
        token = params.get('token', [None])[0]
        
        if not track_id or not token:
            self.wfile.write(json.dumps({'error': 'trackId and token required'}).encode())
            return
        
        # Check cache
        if track_id in TOKEN_CACHE:
            cached = TOKEN_CACHE[track_id]
            if time.time() - cached['time'] < 1800:
                self.wfile.write(json.dumps({'url': cached['url']}).encode())
                return
        
        try:
            from yandex_music import Client
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
                self.wfile.write(json.dumps({'url': url}).encode())
            else:
                self.wfile.write(json.dumps({'error': 'No download info'}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
