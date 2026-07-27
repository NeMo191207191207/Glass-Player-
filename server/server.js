/**
 * Glass Player — Proxy Server
 * 
 * Стриминг аудио из Яндекс Музыки с CORS-поддержкой.
 * 
 * Запуск:
 *   cd server
 *   npm install
 *   node server.js
 * 
 * Сервер запускается на http://localhost:3000
 */

const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Кэш для URL аудио
const audioUrlCache = new Map();
const CACHE_TTL = 30 * 60 * 1000; // 30 минут

// CORS для фронтенда
app.use(cors());
app.use(express.json());

// Раздаём статические файлы из корня проекта
app.use(express.static(path.join(__dirname, '..')));

// Получаем треки из tracks.json
app.get('/api/tracks', (req, res) => {
  const tracksPath = path.join(__dirname, '..', 'tracks.json');
  if (fs.existsSync(tracksPath)) {
    const tracks = JSON.parse(fs.readFileSync(tracksPath, 'utf-8'));
    res.json(tracks);
  } else {
    res.json([]);
  }
});

// Прокси для обложек (чтобы избежать CORS)
app.get('/api/cover/:encoded', async (req, res) => {
  try {
    const url = decodeURIComponent(req.params.encoded);
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    res.set('Content-Type', response.headers.get('content-type'));
    res.set('Cache-Control', 'public, max-age=86400');
    response.body.pipe(res);
  } catch (err) {
    res.status(404).send('Cover not found');
  }
});

// Получение прямого URL аудио из Яндекс Музыки
app.get('/api/audio/:trackId', async (req, res) => {
  const trackId = req.params.trackId;
  const token = req.query.token;

  if (!token) {
    return res.status(400).json({ error: 'Token required' });
  }

  // Проверяем кэш
  const cached = audioUrlCache.get(trackId);
  if (cached && Date.now() - cached.time < CACHE_TTL) {
    return res.json({ url: cached.url });
  }

  try {
    const { execSync } = require('child_process');
    const { writeFileSync, unlinkSync } = require('fs');
    const os = require('os');
    const pathModule = require('path');
    const tmpFile = pathModule.join(os.tmpdir(), `glass_${Date.now()}.py`);
    
    const script = `
import sys, json
from yandex_music import Client
try:
    client = Client('${token}').init()
    track_id, album_id = '${trackId}'.split(':')
    track = client.tracks([f'{track_id}:{album_id}'])[0]
    info = track.get_download_info()
    for d in info:
        if d.codec == 'mp3':
            print(json.dumps({"url": d.get_direct_link()}))
            break
    else:
        if info:
            print(json.dumps({"url": info[0].get_direct_link()}))
        else:
            print(json.dumps({"error": "No download info"}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    
    writeFileSync(tmpFile, script, 'utf-8');
    
    let result;
    try {
      result = execSync(`python "${tmpFile}"`, {
        encoding: 'utf-8',
        timeout: 10000,
        stdio: ['pipe', 'pipe', 'pipe']
      });
    } finally {
      try { unlinkSync(tmpFile); } catch (e) {}
    }

    const jsonMatch = result.match(/\{.*\}/s);
    if (!jsonMatch) {
      return res.status(500).json({ error: 'Invalid response' });
    }

    const data = JSON.parse(jsonMatch[0]);
    
    // Сохраняем в кэш
    if (data.url) {
      audioUrlCache.set(trackId, { url: data.url, time: Date.now() });
    }
    
    res.json(data);
  } catch (err) {
    console.error('Audio URL error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`\n  Glass Player Server`);
  console.log(`  http://localhost:${PORT}`);
  console.log(`  http://localhost:${PORT}/index.html\n`);
});
