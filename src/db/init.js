const fs = require('fs');
const path = require('path');
const pool = require('./connection');
const { seedRegions } = require('./seed-regions');
const { seedBTS } = require('./seed-bts');
const bcrypt = require('bcryptjs');

async function initDatabase() {
  const client = await pool.connect();
  try {
    const schemaSQL = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');
    await client.query(schemaSQL);
    console.log('Database schema created successfully');
  } finally {
    client.release();
  }

  await seedRegions();
  await seedBTS();

  const adminCheck = await pool.query("SELECT id FROM users WHERE role = 'admin'");
  if (adminCheck.rows.length === 0) {
    const { v4: uuidv4 } = require('uuid');
    const adminPass = process.env.ADMIN_PASSWORD || uuidv4().substring(0, 12);
    const hash = await bcrypt.hash(adminPass, 12);
    await pool.query(
      "INSERT INTO users (username, email, password_hash, role, plan) VALUES ('admin', 'admin@bts-indonesia.id', $1, 'admin', 'developer')",
      [hash]
    );
    console.log(`Admin user created - Username: admin, Password: ${adminPass}`);
    console.log('IMPORTANT: Save this password! It will not be shown again.');
  }

  console.log('Database initialization complete');
}

module.exports = { initDatabase };
