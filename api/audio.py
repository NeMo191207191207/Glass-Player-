from http.server import BaseHTTPRequestHandler
import json
import time
import urllib.parse

try:
    from yandex_music import Client
    YM_AVAILABLE = True
except ImportError:
    YM_AVAILABLE = False

TOKEN_CACHE = {}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse query string
        query = {}
        if '?' in self.path:
            qs = self.path.split('?', 1)[1]
            for pair in qs.split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    query[k] = urllib.parse.unquote(v)
        
        track_id = query.get('trackId')
        token = query.get('token')
        
        if not track_id or not token:
            self.wfile.write(json.dumps({'error': 'trackId and token required'}).encode())
            return
        
        if not YM_AVAILABLE:
            self.wfile.write(json.dumps({'error': 'yandex-music not installed'}).encode())
            return
        
        # Check cache
        if track_id in TOKEN_CACHE:
            cached = TOKEN_CACHE[track_id]
            if time.time() - cached['time'] < 1800:
                self.wfile.write(json.dumps({'url': cached['url']}).encode())
                return
        
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
