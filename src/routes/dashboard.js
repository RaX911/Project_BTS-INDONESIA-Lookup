const express = require('express');
const { v4: uuidv4 } = require('uuid');
const pool = require('../db/connection');
const { requireLogin } = require('../middleware/auth');
const router = express.Router();

router.get('/dashboard', requireLogin, async (req, res) => {
  try {
    const user = await pool.query('SELECT * FROM users WHERE id = $1', [req.session.userId]);
    const apiKeys = await pool.query('SELECT * FROM api_keys WHERE user_id = $1 ORDER BY created_at DESC', [req.session.userId]);
    const usageResult = await pool.query(
      `SELECT COUNT(*) as total_requests, 
       COUNT(CASE WHEN created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as today_requests,
       COUNT(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN 1 END) as week_requests
       FROM usage_logs WHERE api_key_id IN (SELECT id FROM api_keys WHERE user_id = $1)`,
      [req.session.userId]
    );
    const towerCount = await pool.query('SELECT COUNT(*) FROM bts_towers');
    const provinceCount = await pool.query('SELECT COUNT(*) FROM provinces');

    res.render('dashboard', {
      user: user.rows[0],
      apiKeys: apiKeys.rows,
      usage: usageResult.rows[0],
      stats: {
        towers: towerCount.rows[0].count,
        provinces: provinceCount.rows[0].count
      },
      session: req.session
    });
  } catch (err) {
    console.error('Dashboard error:', err);
    res.status(500).send('Internal server error');
  }
});

router.post('/api-keys/generate', requireLogin, async (req, res) => {
  const { name } = req.body;
  try {
    const keyCount = await pool.query('SELECT COUNT(*) FROM api_keys WHERE user_id = $1', [req.session.userId]);
    const limits = { free: 2, premium: 5, vip: 10, developer: 100 };
    const maxKeys = limits[req.session.plan] || 2;

    if (parseInt(keyCount.rows[0].count) >= maxKeys) {
      return res.redirect('/dashboard?error=Batas+maksimal+API+key+tercapai');
    }

    const apiKey = 'bts_' + uuidv4().replace(/-/g, '') + uuidv4().replace(/-/g, '').substring(0, 16);
    await pool.query(
      'INSERT INTO api_keys (user_id, api_key, name) VALUES ($1, $2, $3)',
      [req.session.userId, apiKey, name || 'Default']
    );
    res.redirect('/dashboard?success=API+key+berhasil+dibuat');
  } catch (err) {
    console.error('Generate API key error:', err);
    res.redirect('/dashboard?error=Gagal+membuat+API+key');
  }
});

router.post('/api-keys/:id/toggle', requireLogin, async (req, res) => {
  try {
    await pool.query(
      'UPDATE api_keys SET is_active = NOT is_active WHERE id = $1 AND user_id = $2',
      [req.params.id, req.session.userId]
    );
    res.redirect('/dashboard');
  } catch (err) {
    console.error('Toggle API key error:', err);
    res.redirect('/dashboard?error=Gagal+mengubah+status+API+key');
  }
});

router.post('/api-keys/:id/delete', requireLogin, async (req, res) => {
  try {
    await pool.query('DELETE FROM api_keys WHERE id = $1 AND user_id = $2', [req.params.id, req.session.userId]);
    res.redirect('/dashboard?success=API+key+berhasil+dihapus');
  } catch (err) {
    console.error('Delete API key error:', err);
    res.redirect('/dashboard?error=Gagal+menghapus+API+key');
  }
});

router.get('/usage', requireLogin, async (req, res) => {
  try {
    const user = await pool.query('SELECT * FROM users WHERE id = $1', [req.session.userId]);
    const logs = await pool.query(
      `SELECT ul.*, ak.name as key_name, ak.api_key 
       FROM usage_logs ul 
       JOIN api_keys ak ON ul.api_key_id = ak.id 
       WHERE ak.user_id = $1 
       ORDER BY ul.created_at DESC LIMIT 100`,
      [req.session.userId]
    );
    const dailyStats = await pool.query(
      `SELECT DATE(ul.created_at) as date, COUNT(*) as count 
       FROM usage_logs ul 
       JOIN api_keys ak ON ul.api_key_id = ak.id 
       WHERE ak.user_id = $1 AND ul.created_at > NOW() - INTERVAL '30 days'
       GROUP BY DATE(ul.created_at) ORDER BY date DESC`,
      [req.session.userId]
    );
    res.render('usage', {
      user: user.rows[0],
      logs: logs.rows,
      dailyStats: dailyStats.rows,
      session: req.session
    });
  } catch (err) {
    console.error('Usage error:', err);
    res.status(500).send('Internal server error');
  }
});

module.exports = router;
