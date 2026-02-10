const express = require('express');
const pool = require('../db/connection');
const { requireLogin } = require('../middleware/auth');
const router = express.Router();

router.get('/', (req, res) => {
  if (req.session.userId) return res.redirect('/dashboard');
  res.render('home', { session: req.session });
});

router.get('/pricing', (req, res) => {
  res.render('pricing', { session: req.session });
});

router.get('/docs', (req, res) => {
  res.render('docs', { session: req.session });
});

router.get('/towers', requireLogin, async (req, res) => {
  try {
    const { province, mnc, signal_type, page = 1 } = req.query;
    const limit = 25;
    const offset = (parseInt(page) - 1) * limit;

    let where = [];
    let params = [];
    let idx = 1;
    if (province) { where.push(`b.province_code = $${idx++}`); params.push(province); }
    if (mnc) { where.push(`b.mnc = $${idx++}`); params.push(mnc); }
    if (signal_type) { where.push(`b.signal_type = $${idx++}`); params.push(signal_type); }

    const whereClause = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';

    const countResult = await pool.query(`SELECT COUNT(*) FROM bts_towers b ${whereClause}`, params);
    const total = parseInt(countResult.rows[0].count);

    params.push(limit, offset);
    const towers = await pool.query(
      `SELECT b.*, p.name as province_name, k.name as kabupaten_name 
       FROM bts_towers b 
       LEFT JOIN provinces p ON b.province_code = p.code 
       LEFT JOIN kabupaten k ON b.kabupaten_code = k.code 
       ${whereClause} ORDER BY b.id LIMIT $${idx++} OFFSET $${idx++}`,
      params
    );

    const provinces = await pool.query('SELECT * FROM provinces ORDER BY name');
    const operators = await pool.query('SELECT DISTINCT mnc, brand FROM operators ORDER BY brand');

    res.render('towers', {
      towers: towers.rows,
      provinces: provinces.rows,
      operators: operators.rows,
      pagination: { page: parseInt(page), total, totalPages: Math.ceil(total / limit), limit },
      filters: { province, mnc, signal_type },
      session: req.session
    });
  } catch (err) {
    console.error('Towers page error:', err);
    res.status(500).send('Internal server error');
  }
});

router.get('/lookup', requireLogin, (req, res) => {
  res.render('lookup', { session: req.session, result: null, error: null });
});

router.post('/lookup', requireLogin, async (req, res) => {
  const { msisdn } = req.body;
  try {
    const apiKey = await pool.query('SELECT api_key FROM api_keys WHERE user_id = $1 AND is_active = true LIMIT 1', [req.session.userId]);

    if (apiKey.rows.length === 0) {
      return res.render('lookup', { session: req.session, result: null, error: 'Anda belum memiliki API key aktif. Buat di Dashboard.' });
    }

    const http = require('http');
    const port = process.env.PORT || 5000;

    const options = {
      hostname: '127.0.0.1',
      port: port,
      path: `/api/v1/msisdn/${encodeURIComponent(msisdn)}`,
      method: 'GET',
      headers: { 'X-API-Key': apiKey.rows[0].api_key }
    };

    const apiReq = http.request(options, (apiRes) => {
      let data = '';
      apiRes.on('data', (chunk) => data += chunk);
      apiRes.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.error) {
            res.render('lookup', { session: req.session, result: null, error: result.error });
          } else {
            res.render('lookup', { session: req.session, result: result.data, error: null });
          }
        } catch (e) {
          res.render('lookup', { session: req.session, result: null, error: 'Gagal memproses respons' });
        }
      });
    });

    apiReq.on('error', (err) => {
      console.error('Lookup request error:', err);
      res.render('lookup', { session: req.session, result: null, error: 'Gagal menghubungi API' });
    });

    apiReq.end();
  } catch (err) {
    console.error('Lookup error:', err);
    res.render('lookup', { session: req.session, result: null, error: 'Terjadi kesalahan' });
  }
});

module.exports = router;
