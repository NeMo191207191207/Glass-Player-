const { YandexMusicClient } = require('yandex-music');

// Simple in-memory cache
const cache = new Map();
const CACHE_TTL = 30 * 60 * 1000; // 30 min

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  
  const { trackId, token } = req.query;
  
  if (!trackId || !token) {
    return res.status(400).json({ error: 'trackId and token required' });
  }
  
  // Check cache
  const cached = cache.get(trackId);
  if (cached && Date.now() - cached.time < CACHE_TTL) {
    return res.json({ url: cached.url });
  }
  
  try {
    const client = new YandexMusicClient({ token });
    
    const [id, albumId] = trackId.split(':');
    const tracks = await client.tracks([`${id}:${albumId}`]);
    const track = tracks[0];
    const info = await track.getDownloadInfo();
    
    // Find mp3 or first available
    const mp3 = info.find(d => d.codec === 'mp3') || info[0];
    if (!mp3) {
      return res.status(404).json({ error: 'No download info' });
    }
    
    const url = await mp3.getDirectLink();
    
    // Cache it
    cache.set(trackId, { url, time: Date.now() });
    
    res.json({ url });
  } catch (e) {
    console.error('Audio URL error:', e.message);
    res.status(500).json({ error: e.message });
  }
};
