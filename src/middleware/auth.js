const pool = require('../db/connection');

function requireLogin(req, res, next) {
  if (req.session && req.session.userId) {
    return next();
  }
  if (req.headers.accept && req.headers.accept.includes('application/json')) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  res.redirect('/login');
}

function requireAdmin(req, res, next) {
  if (req.session && req.session.userId && req.session.role === 'admin') {
    return next();
  }
  if (req.headers.accept && req.headers.accept.includes('application/json')) {
    return res.status(403).json({ error: 'Admin access required' });
  }
  res.redirect('/login');
}

async function apiKeyAuth(req, res, next) {
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  if (!apiKey) {
    return res.status(401).json({ error: 'API key required. Provide via X-API-Key header or api_key query parameter.' });
  }

  try {
    const result = await pool.query(
      `SELECT ak.*, u.plan, u.role FROM api_keys ak
       JOIN users u ON ak.user_id = u.id
       WHERE ak.api_key = $1 AND ak.is_active = true`,
      [apiKey]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid or inactive API key' });
    }

    const keyData = result.rows[0];
    const limits = { free: 100, premium: 1000, vip: 10000, developer: 999999 };
    const dailyLimit = limits[keyData.plan] || 100;

    if (keyData.requests_today >= dailyLimit) {
      return res.status(429).json({
        error: 'Daily API limit exceeded',
        limit: dailyLimit,
        used: keyData.requests_today,
        plan: keyData.plan
      });
    }

    await pool.query(
      'UPDATE api_keys SET requests_today = requests_today + 1, requests_total = requests_total + 1, last_used_at = NOW() WHERE id = $1',
      [keyData.id]
    );

    req.apiKeyData = keyData;
    next();
  } catch (err) {
    console.error('API key auth error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
}

module.exports = { requireLogin, requireAdmin, apiKeyAuth };
