const pool = require('./connection');

const provinceCenters = {
  '11': { lat: 5.5483, lng: 95.3238, name: 'Aceh' },
  '12': { lat: 3.5952, lng: 98.6722, name: 'Sumatera Utara' },
  '13': { lat: -0.9471, lng: 100.4172, name: 'Sumatera Barat' },
  '14': { lat: 0.5071, lng: 101.4478, name: 'Riau' },
  '15': { lat: -1.6101, lng: 103.6131, name: 'Jambi' },
  '16': { lat: -2.9761, lng: 104.7754, name: 'Sumatera Selatan' },
  '17': { lat: -3.7928, lng: 102.2608, name: 'Bengkulu' },
  '18': { lat: -5.4500, lng: 105.2667, name: 'Lampung' },
  '19': { lat: -2.1214, lng: 106.1169, name: 'Bangka Belitung' },
  '21': { lat: 1.0456, lng: 104.0305, name: 'Kepulauan Riau' },
  '31': { lat: -6.2088, lng: 106.8456, name: 'DKI Jakarta' },
  '32': { lat: -6.9175, lng: 107.6191, name: 'Jawa Barat' },
  '33': { lat: -7.1510, lng: 110.1403, name: 'Jawa Tengah' },
  '34': { lat: -7.7956, lng: 110.3695, name: 'DI Yogyakarta' },
  '35': { lat: -7.5361, lng: 112.2384, name: 'Jawa Timur' },
  '36': { lat: -6.4058, lng: 106.0640, name: 'Banten' },
  '51': { lat: -8.3405, lng: 115.0920, name: 'Bali' },
  '52': { lat: -8.6529, lng: 117.3616, name: 'NTB' },
  '53': { lat: -8.6574, lng: 121.0794, name: 'NTT' },
  '61': { lat: -0.0263, lng: 109.3425, name: 'Kalimantan Barat' },
  '62': { lat: -1.6815, lng: 113.3824, name: 'Kalimantan Tengah' },
  '63': { lat: -3.0926, lng: 115.2838, name: 'Kalimantan Selatan' },
  '64': { lat: -1.2654, lng: 116.8311, name: 'Kalimantan Timur' },
  '65': { lat: 3.0731, lng: 116.0413, name: 'Kalimantan Utara' },
  '71': { lat: 1.4748, lng: 124.8421, name: 'Sulawesi Utara' },
  '72': { lat: -1.4300, lng: 121.4456, name: 'Sulawesi Tengah' },
  '73': { lat: -3.6688, lng: 119.9741, name: 'Sulawesi Selatan' },
  '74': { lat: -4.1448, lng: 122.1748, name: 'Sulawesi Tenggara' },
  '75': { lat: 0.6999, lng: 122.4467, name: 'Gorontalo' },
  '76': { lat: -2.8442, lng: 119.2321, name: 'Sulawesi Barat' },
  '81': { lat: -3.2385, lng: 130.1453, name: 'Maluku' },
  '82': { lat: 1.5709, lng: 127.8088, name: 'Maluku Utara' },
  '91': { lat: -4.2699, lng: 138.0804, name: 'Papua' },
  '92': { lat: -1.3361, lng: 133.1747, name: 'Papua Barat' },
  '93': { lat: -6.5000, lng: 140.0000, name: 'Papua Selatan' },
  '94': { lat: -3.5000, lng: 136.5000, name: 'Papua Tengah' },
  '95': { lat: -4.0000, lng: 139.0000, name: 'Papua Pegunungan' },
  '96': { lat: -1.5000, lng: 132.0000, name: 'Papua Barat Daya' },
};

const operatorMNCs = ['10', '01', '11', '89', '28', '08'];
const signalTypes = ['2G', '3G', '4G', '5G'];

function seededRandom(seed) {
  let s = seed;
  return function() {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}

async function seedBTS() {
  const client = await pool.connect();
  try {
    const existingCount = await client.query('SELECT COUNT(*) FROM bts_towers');
    if (parseInt(existingCount.rows[0].count) > 0) {
      console.log(`BTS towers already seeded (${existingCount.rows[0].count} records). Skipping.`);
      return;
    }

    await client.query('BEGIN');

    const kabResult = await client.query('SELECT code, province_code, name FROM kabupaten');
    const kabupatenList = kabResult.rows;

    let totalTowers = 0;
    const batchSize = 500;
    let values = [];
    let paramCount = 0;
    let params = [];

    for (const kab of kabupatenList) {
      const prov = provinceCenters[kab.province_code];
      if (!prov) continue;

      const rand = seededRandom(parseInt(kab.code) * 7919);
      const isUrban = kab.name.startsWith('Kota');
      const towerCount = isUrban ? 40 + Math.floor(rand() * 60) : 15 + Math.floor(rand() * 35);

      for (let i = 0; i < towerCount; i++) {
        const mnc = operatorMNCs[Math.floor(rand() * operatorMNCs.length)];
        const cellId = 10000 + Math.floor(rand() * 55000);
        const lac = 1000 + Math.floor(rand() * 30000);
        const latOffset = (rand() - 0.5) * 0.8;
        const lngOffset = (rand() - 0.5) * 0.8;
        const lat = prov.lat + latOffset;
        const lng = prov.lng + lngOffset;
        const sigIdx = isUrban ? Math.min(Math.floor(rand() * 4), 3) : Math.floor(rand() * 3);
        const signalType = signalTypes[sigIdx];
        const height = 15 + Math.floor(rand() * 55);
        const azimuth = Math.floor(rand() * 360);
        const power = -40 - Math.floor(rand() * 60);

        const base = paramCount;
        values.push(`($${base+1},$${base+2},$${base+3},$${base+4},$${base+5},$${base+6},$${base+7},$${base+8},$${base+9},$${base+10},$${base+11},$${base+12})`);
        params.push(cellId, lac, '510', mnc, lat, lng, signalType, kab.province_code, kab.code, `${kab.name}, ${prov.name}`, height, azimuth);
        paramCount += 12;
        totalTowers++;

        if (values.length >= batchSize) {
          const sql = `INSERT INTO bts_towers (cell_id, lac, mcc, mnc, latitude, longitude, signal_type, province_code, kabupaten_code, address, tower_height, azimuth) VALUES ${values.join(',')}`;
          await client.query(sql, params);
          values = [];
          params = [];
          paramCount = 0;
        }
      }
    }

    if (values.length > 0) {
      const sql = `INSERT INTO bts_towers (cell_id, lac, mcc, mnc, latitude, longitude, signal_type, province_code, kabupaten_code, address, tower_height, azimuth) VALUES ${values.join(',')}`;
      await client.query(sql, params);
    }

    await client.query('COMMIT');
    console.log(`Seeded ${totalTowers} BTS towers across all kabupaten/kota`);
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

module.exports = { seedBTS };
