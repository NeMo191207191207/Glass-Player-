const { readFileSync, existsSync } = require('fs');
const { join } = require('path');

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate');
  
  const tracksPath = join(process.cwd(), 'tracks.json');
  if (existsSync(tracksPath)) {
    const tracks = JSON.parse(readFileSync(tracksPath, 'utf-8'));
    res.json(tracks);
  } else {
    res.json([]);
  }
};
