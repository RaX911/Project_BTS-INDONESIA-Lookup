const express = require('express');
const bcrypt = require('bcryptjs');
const pool = require('../db/connection');
const router = express.Router();

router.get('/login', (req, res) => {
  if (req.session.userId) return res.redirect('/dashboard');
  res.render('login', { error: null, success: null });
});

router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const result = await pool.query('SELECT * FROM users WHERE username = $1 OR email = $1', [username]);
    if (result.rows.length === 0) {
      return res.render('login', { error: 'Username atau password salah', success: null });
    }
    const user = result.rows[0];
    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) {
      return res.render('login', { error: 'Username atau password salah', success: null });
    }
    req.session.userId = user.id;
    req.session.username = user.username;
    req.session.role = user.role;
    req.session.plan = user.plan;
    res.redirect('/dashboard');
  } catch (err) {
    console.error('Login error:', err);
    res.render('login', { error: 'Terjadi kesalahan', success: null });
  }
});

router.get('/register', (req, res) => {
  if (req.session.userId) return res.redirect('/dashboard');
  res.render('register', { error: null });
});

router.post('/register', async (req, res) => {
  const { username, email, password, confirmPassword } = req.body;
  if (password !== confirmPassword) {
    return res.render('register', { error: 'Password tidak cocok' });
  }
  if (password.length < 6) {
    return res.render('register', { error: 'Password minimal 6 karakter' });
  }
  try {
    const exists = await pool.query('SELECT id FROM users WHERE username = $1 OR email = $2', [username, email]);
    if (exists.rows.length > 0) {
      return res.render('register', { error: 'Username atau email sudah terdaftar' });
    }
    const hash = await bcrypt.hash(password, 10);
    await pool.query(
      'INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3)',
      [username, email, hash]
    );
    res.render('login', { error: null, success: 'Registrasi berhasil! Silakan login.' });
  } catch (err) {
    console.error('Register error:', err);
    res.render('register', { error: 'Terjadi kesalahan saat registrasi' });
  }
});

router.get('/logout', (req, res) => {
  req.session.destroy(() => {
    res.redirect('/login');
  });
});

module.exports = router;
