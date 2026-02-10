CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  plan VARCHAR(20) DEFAULT 'free' CHECK (plan IN ('free', 'premium', 'vip', 'developer')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  api_key VARCHAR(64) UNIQUE NOT NULL,
  name VARCHAR(100) DEFAULT 'Default',
  is_active BOOLEAN DEFAULT TRUE,
  requests_today INTEGER DEFAULT 0,
  requests_total INTEGER DEFAULT 0,
  last_used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS provinces (
  id SERIAL PRIMARY KEY,
  code VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS kabupaten (
  id SERIAL PRIMARY KEY,
  code VARCHAR(10) UNIQUE NOT NULL,
  province_code VARCHAR(10) REFERENCES provinces(code),
  name VARCHAR(150) NOT NULL,
  type VARCHAR(20) DEFAULT 'kabupaten'
);

CREATE TABLE IF NOT EXISTS kecamatan (
  id SERIAL PRIMARY KEY,
  code VARCHAR(15) UNIQUE NOT NULL,
  kabupaten_code VARCHAR(10) REFERENCES kabupaten(code),
  name VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS kelurahan (
  id SERIAL PRIMARY KEY,
  code VARCHAR(20) UNIQUE NOT NULL,
  kecamatan_code VARCHAR(15) REFERENCES kecamatan(code),
  name VARCHAR(150) NOT NULL,
  type VARCHAR(20) DEFAULT 'kelurahan'
);

CREATE TABLE IF NOT EXISTS operators (
  id SERIAL PRIMARY KEY,
  mcc VARCHAR(5) NOT NULL DEFAULT '510',
  mnc VARCHAR(5) NOT NULL,
  name VARCHAR(100) NOT NULL,
  brand VARCHAR(100),
  UNIQUE(mcc, mnc)
);

CREATE TABLE IF NOT EXISTS bts_towers (
  id SERIAL PRIMARY KEY,
  cell_id INTEGER NOT NULL,
  lac INTEGER NOT NULL,
  mcc VARCHAR(5) NOT NULL DEFAULT '510',
  mnc VARCHAR(5) NOT NULL,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  signal_type VARCHAR(10) DEFAULT '4G',
  province_code VARCHAR(10),
  kabupaten_code VARCHAR(10),
  kecamatan_code VARCHAR(15),
  address TEXT,
  tower_height DOUBLE PRECISION,
  azimuth INTEGER,
  power_dbm INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bts_cell_lac ON bts_towers(cell_id, lac);
CREATE INDEX IF NOT EXISTS idx_bts_mcc_mnc ON bts_towers(mcc, mnc);
CREATE INDEX IF NOT EXISTS idx_bts_province ON bts_towers(province_code);
CREATE INDEX IF NOT EXISTS idx_bts_coords ON bts_towers(latitude, longitude);

CREATE TABLE IF NOT EXISTS msisdn_prefixes (
  id SERIAL PRIMARY KEY,
  prefix VARCHAR(10) NOT NULL,
  operator_name VARCHAR(100) NOT NULL,
  mnc VARCHAR(5) NOT NULL,
  network_type VARCHAR(20) DEFAULT 'GSM'
);

CREATE TABLE IF NOT EXISTS usage_logs (
  id SERIAL PRIMARY KEY,
  api_key_id INTEGER REFERENCES api_keys(id) ON DELETE CASCADE,
  endpoint VARCHAR(255) NOT NULL,
  msisdn VARCHAR(20),
  response_status INTEGER,
  ip_address VARCHAR(45),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_api_key ON usage_logs(api_key_id);
CREATE INDEX IF NOT EXISTS idx_usage_created ON usage_logs(created_at);

CREATE TABLE IF NOT EXISTS session (
  sid VARCHAR NOT NULL COLLATE "default",
  sess JSON NOT NULL,
  expire TIMESTAMP(6) NOT NULL,
  PRIMARY KEY (sid)
);
CREATE INDEX IF NOT EXISTS idx_session_expire ON session(expire);
