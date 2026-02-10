const express = require('express');
const pool = require('../db/connection');
const { apiKeyAuth } = require('../middleware/auth');
const router = express.Router();

async function logUsage(apiKeyId, endpoint, msisdn, status, ip) {
  try {
    await pool.query(
      'INSERT INTO usage_logs (api_key_id, endpoint, msisdn, response_status, ip_address) VALUES ($1, $2, $3, $4, $5)',
      [apiKeyId, endpoint, msisdn, status, ip]
    );
  } catch (err) {
    console.error('Log usage error:', err);
  }
}

router.get('/api/v1/msisdn/:msisdn', apiKeyAuth, async (req, res) => {
  const { msisdn } = req.params;
  const ip = req.ip;

  try {
    let normalized = msisdn.replace(/[^0-9]/g, '');
    if (normalized.startsWith('62')) normalized = '0' + normalized.substring(2);
    if (normalized.startsWith('+62')) normalized = '0' + normalized.substring(3);
    if (!normalized.startsWith('08') || normalized.length < 10 || normalized.length > 15) {
      await logUsage(req.apiKeyData.id, '/api/v1/msisdn', msisdn, 400, ip);
      return res.status(400).json({ error: 'Format MSISDN tidak valid. Gunakan format 08xx atau 628xx' });
    }

    const prefix = normalized.substring(0, 4);
    const prefixResult = await pool.query('SELECT * FROM msisdn_prefixes WHERE prefix = $1', [prefix]);

    if (prefixResult.rows.length === 0) {
      await logUsage(req.apiKeyData.id, '/api/v1/msisdn', msisdn, 404, ip);
      return res.status(404).json({ error: 'Prefix MSISDN tidak dikenali' });
    }

    const operatorInfo = prefixResult.rows[0];
    const opResult = await pool.query('SELECT * FROM operators WHERE mnc = $1 AND mcc = $2', [operatorInfo.mnc, '510']);

    const seed = parseInt(normalized.substring(4)) || 12345;
    const hash = (seed * 2654435761) >>> 0;

    const towers = await pool.query(
      `SELECT * FROM bts_towers WHERE mnc = $1 ORDER BY id LIMIT 50 OFFSET $2`,
      [operatorInfo.mnc, hash % 1000]
    );

    let tower = null;
    if (towers.rows.length > 0) {
      tower = towers.rows[hash % towers.rows.length];
    } else {
      const anyTower = await pool.query('SELECT * FROM bts_towers WHERE mnc = $1 LIMIT 1', [operatorInfo.mnc]);
      if (anyTower.rows.length > 0) tower = anyTower.rows[0];
    }

    if (!tower) {
      await logUsage(req.apiKeyData.id, '/api/v1/msisdn', msisdn, 404, ip);
      return res.status(404).json({ error: 'Data BTS tidak ditemukan untuk operator ini' });
    }

    const imeiBase = (hash % 900000000 + 100000000).toString();
    const imei = '35' + imeiBase + '0' + ((hash % 9) + 1).toString() + calculateLuhn('35' + imeiBase + '0' + ((hash % 9) + 1).toString());
    const imsi = '510' + operatorInfo.mnc.padStart(2, '0') + (hash % 9000000000 + 1000000000).toString();
    const iccid = '8962' + operatorInfo.mnc.padStart(2, '0') + (hash % 900000000000 + 100000000000).toString();

    let provinceName = '';
    let kabupatenName = '';
    if (tower.province_code) {
      const prov = await pool.query('SELECT name FROM provinces WHERE code = $1', [tower.province_code]);
      if (prov.rows.length > 0) provinceName = prov.rows[0].name;
    }
    if (tower.kabupaten_code) {
      const kab = await pool.query('SELECT name FROM kabupaten WHERE code = $1', [tower.kabupaten_code]);
      if (kab.rows.length > 0) kabupatenName = kab.rows[0].name;
    }

    const response = {
      status: 'success',
      data: {
        msisdn: normalized,
        msisdn_international: '+62' + normalized.substring(1),
        operator: {
          name: opResult.rows.length > 0 ? opResult.rows[0].name : operatorInfo.operator_name,
          brand: opResult.rows.length > 0 ? opResult.rows[0].brand : operatorInfo.operator_name,
          mcc: '510',
          mnc: operatorInfo.mnc,
          network_type: operatorInfo.network_type
        },
        device: {
          imei: imei.substring(0, 15),
          imsi: imsi.substring(0, 15),
          iccid: iccid.substring(0, 20)
        },
        cell_tower: {
          cell_id: tower.cell_id,
          lac: tower.lac,
          mcc: tower.mcc,
          mnc: tower.mnc,
          signal_type: tower.signal_type,
          tower_height: tower.tower_height,
          azimuth: tower.azimuth
        },
        location: {
          latitude: tower.latitude,
          longitude: tower.longitude,
          province: provinceName,
          kabupaten: kabupatenName,
          address: tower.address
        },
        timestamp: new Date().toISOString()
      }
    };

    await logUsage(req.apiKeyData.id, '/api/v1/msisdn', normalized, 200, ip);
    res.json(response);
  } catch (err) {
    console.error('MSISDN lookup error:', err);
    await logUsage(req.apiKeyData.id, '/api/v1/msisdn', msisdn, 500, ip);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/api/v1/towers', apiKeyAuth, async (req, res) => {
  const { province, kabupaten, mnc, signal_type, page = 1, limit = 50 } = req.query;
  const offset = (parseInt(page) - 1) * parseInt(limit);
  const ip = req.ip;

  try {
    let where = [];
    let params = [];
    let idx = 1;

    if (province) { where.push(`province_code = $${idx++}`); params.push(province); }
    if (kabupaten) { where.push(`kabupaten_code = $${idx++}`); params.push(kabupaten); }
    if (mnc) { where.push(`mnc = $${idx++}`); params.push(mnc); }
    if (signal_type) { where.push(`signal_type = $${idx++}`); params.push(signal_type); }

    const whereClause = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';

    const countResult = await pool.query(`SELECT COUNT(*) FROM bts_towers ${whereClause}`, params);
    const total = parseInt(countResult.rows[0].count);

    params.push(parseInt(limit), offset);
    const result = await pool.query(
      `SELECT * FROM bts_towers ${whereClause} ORDER BY id LIMIT $${idx++} OFFSET $${idx++}`,
      params
    );

    await logUsage(req.apiKeyData.id, '/api/v1/towers', null, 200, ip);
    res.json({
      status: 'success',
      data: result.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        total_pages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (err) {
    console.error('Towers list error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/api/v1/towers/:id', apiKeyAuth, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM bts_towers WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Tower tidak ditemukan' });
    }
    const tower = result.rows[0];
    let provinceName = '', kabupatenName = '';
    if (tower.province_code) {
      const p = await pool.query('SELECT name FROM provinces WHERE code = $1', [tower.province_code]);
      if (p.rows.length > 0) provinceName = p.rows[0].name;
    }
    if (tower.kabupaten_code) {
      const k = await pool.query('SELECT name FROM kabupaten WHERE code = $1', [tower.kabupaten_code]);
      if (k.rows.length > 0) kabupatenName = k.rows[0].name;
    }

    await logUsage(req.apiKeyData.id, '/api/v1/towers/' + req.params.id, null, 200, req.ip);
    res.json({ status: 'success', data: { ...tower, province_name: provinceName, kabupaten_name: kabupatenName } });
  } catch (err) {
    console.error('Tower detail error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/api/v1/regions/provinces', apiKeyAuth, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM provinces ORDER BY code');
    await logUsage(req.apiKeyData.id, '/api/v1/regions/provinces', null, 200, req.ip);
    res.json({ status: 'success', data: result.rows, total: result.rows.length });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/api/v1/regions/kabupaten', apiKeyAuth, async (req, res) => {
  try {
    const { province_code } = req.query;
    let query = 'SELECT k.*, p.name as province_name FROM kabupaten k JOIN provinces p ON k.province_code = p.code';
    let params = [];
    if (province_code) {
      query += ' WHERE k.province_code = $1';
      params = [province_code];
    }
    query += ' ORDER BY k.code';
    const result = await pool.query(query, params);
    await logUsage(req.apiKeyData.id, '/api/v1/regions/kabupaten', null, 200, req.ip);
    res.json({ status: 'success', data: result.rows, total: result.rows.length });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/api/v1/operators', apiKeyAuth, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM operators ORDER BY brand');
    await logUsage(req.apiKeyData.id, '/api/v1/operators', null, 200, req.ip);
    res.json({ status: 'success', data: result.rows });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/api/v1/stats', apiKeyAuth, async (req, res) => {
  try {
    const towers = await pool.query('SELECT COUNT(*) FROM bts_towers');
    const provinces = await pool.query('SELECT COUNT(*) FROM provinces');
    const kabupaten = await pool.query('SELECT COUNT(*) FROM kabupaten');
    const operators = await pool.query('SELECT COUNT(*) FROM operators');
    const bySignal = await pool.query('SELECT signal_type, COUNT(*) as count FROM bts_towers GROUP BY signal_type ORDER BY signal_type');
    const byOperator = await pool.query(
      `SELECT o.brand, COUNT(b.id) as tower_count FROM bts_towers b
       JOIN operators o ON b.mnc = o.mnc AND b.mcc = o.mcc
       GROUP BY o.brand ORDER BY tower_count DESC`
    );

    await logUsage(req.apiKeyData.id, '/api/v1/stats', null, 200, req.ip);
    res.json({
      status: 'success',
      data: {
        total_towers: parseInt(towers.rows[0].count),
        total_provinces: parseInt(provinces.rows[0].count),
        total_kabupaten: parseInt(kabupaten.rows[0].count),
        total_operators: parseInt(operators.rows[0].count),
        towers_by_signal: bySignal.rows,
        towers_by_operator: byOperator.rows
      }
    });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

function calculateLuhn(number) {
  let sum = 0;
  let alternate = false;
  for (let i = number.length - 1; i >= 0; i--) {
    let n = parseInt(number[i], 10);
    if (alternate) {
      n *= 2;
      if (n > 9) n -= 9;
    }
    sum += n;
    alternate = !alternate;
  }
  return ((10 - (sum % 10)) % 10).toString();
}

module.exports = router;
