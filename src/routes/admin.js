const express = require('express');
const bcrypt = require('bcryptjs');
const pool = require('../db/connection');
const { requireAdmin } = require('../middleware/auth');
const router = express.Router();

router.get('/admin', requireAdmin, async (req, res) => {
  try {
    const users = await pool.query('SELECT id, username, email, role, plan, created_at FROM users ORDER BY created_at DESC');
    const towerCount = await pool.query('SELECT COUNT(*) FROM bts_towers');
    const userCount = await pool.query('SELECT COUNT(*) FROM users');
    const keyCount = await pool.query('SELECT COUNT(*) FROM api_keys');
    const todayUsage = await pool.query("SELECT COUNT(*) FROM usage_logs WHERE created_at > NOW() - INTERVAL '24 hours'");
    const byPlan = await pool.query('SELECT plan, COUNT(*) as count FROM users GROUP BY plan');
    const recentLogs = await pool.query(
      `SELECT ul.*, ak.name as key_name, u.username 
       FROM usage_logs ul 
       JOIN api_keys ak ON ul.api_key_id = ak.id 
       JOIN users u ON ak.user_id = u.id 
       ORDER BY ul.created_at DESC LIMIT 50`
    );

    res.render('admin', {
      users: users.rows,
      stats: {
        towers: towerCount.rows[0].count,
        users: userCount.rows[0].count,
        apiKeys: keyCount.rows[0].count,
        todayUsage: todayUsage.rows[0].count,
        byPlan: byPlan.rows
      },
      recentLogs: recentLogs.rows,
      session: req.session
    });
  } catch (err) {
    console.error('Admin error:', err);
    res.status(500).send('Internal server error');
  }
});

router.post('/admin/users/:id/plan', requireAdmin, async (req, res) => {
  const { plan } = req.body;
  try {
    await pool.query('UPDATE users SET plan = $1, updated_at = NOW() WHERE id = $2', [plan, req.params.id]);
    res.redirect('/admin?success=Plan+berhasil+diubah');
  } catch (err) {
    console.error('Update plan error:', err);
    res.redirect('/admin?error=Gagal+mengubah+plan');
  }
});

router.post('/admin/users/:id/role', requireAdmin, async (req, res) => {
  const { role } = req.body;
  try {
    await pool.query('UPDATE users SET role = $1, updated_at = NOW() WHERE id = $2', [role, req.params.id]);
    res.redirect('/admin?success=Role+berhasil+diubah');
  } catch (err) {
    console.error('Update role error:', err);
    res.redirect('/admin?error=Gagal+mengubah+role');
  }
});

router.post('/admin/users/:id/delete', requireAdmin, async (req, res) => {
  try {
    if (parseInt(req.params.id) === req.session.userId) {
      return res.redirect('/admin?error=Tidak+bisa+menghapus+akun+sendiri');
    }
    await pool.query('DELETE FROM users WHERE id = $1', [req.params.id]);
    res.redirect('/admin?success=User+berhasil+dihapus');
  } catch (err) {
    console.error('Delete user error:', err);
    res.redirect('/admin?error=Gagal+menghapus+user');
  }
});

router.post('/admin/reset-daily', requireAdmin, async (req, res) => {
  try {
    await pool.query('UPDATE api_keys SET requests_today = 0');
    res.redirect('/admin?success=Reset+daily+counter+berhasil');
  } catch (err) {
    res.redirect('/admin?error=Gagal+reset+counter');
  }
});

module.exports = router;
