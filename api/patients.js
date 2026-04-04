import { put, list } from '@vercel/blob';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Password');

  if (req.method === 'OPTIONS') return res.status(200).end();

  if (req.headers['x-password'] !== process.env.HDR_PASSWORD) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (req.method === 'GET') {
    try {
      const { blobs } = await list({ prefix: 'patients' });
      if (blobs.length === 0) return res.status(200).json(null);
      const r = await fetch(blobs[0].url);
      return res.status(200).json(await r.json());
    } catch {
      return res.status(200).json(null);
    }
  }

  if (req.method === 'POST') {
    await put('patients', JSON.stringify(req.body), {
      access: 'public',
      contentType: 'application/json',
      addRandomSuffix: false,
    });
    return res.status(200).json({ ok: true });
  }

  res.status(405).end();
}
