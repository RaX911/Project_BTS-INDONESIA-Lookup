# BTS Indonesia Cell Tower API

## Overview
Platform API untuk database BTS Cell Tower seluruh Indonesia. Menyediakan data Cell ID, LAC, MCC, MNC, IMEI, IMSI, ICCID, koordinat, dan informasi operator melalui REST API.

## Architecture
- **Backend**: Node.js + Express.js
- **Database**: PostgreSQL (Neon-backed via Replit)
- **Template Engine**: EJS
- **Authentication**: Session-based with bcrypt password hashing
- **API Auth**: API key-based authentication

## Project Structure
```
server.js              - Main application entry point
src/
  db/
    connection.js      - PostgreSQL connection pool
    schema.sql         - Database schema
    init.js            - Database initialization
    seed-regions.js    - Indonesian regions seed data
    seed-bts.js        - BTS tower seed data
  middleware/
    auth.js            - Authentication middleware
  routes/
    auth.js            - Login/Register routes
    dashboard.js       - Dashboard & API key management
    api.js             - REST API endpoints
    admin.js           - Admin panel routes
    pages.js           - Static pages & MSISDN lookup
  views/
    partials/          - Header/Footer templates
    *.ejs              - Page templates
```

## Features
- User registration & login
- API key generation & management
- MSISDN lookup (all Indonesian operators)
- BTS Tower database (all 38 provinces, 500+ kabupaten/kota)
- Usage tracking & analytics
- Admin panel (user management, plan management)
- Pricing plans (Free/Premium/VIP/Developer)
- Full REST API with documentation

## Database
- 38 provinces of Indonesia
- 500+ kabupaten/kota
- 10,000+ BTS tower records
- All major Indonesian operators (Telkomsel, Indosat, XL, Tri, Smartfren, Axis)
- MSISDN prefix mapping

## Default Admin Account
- Username: admin
- Password: admin123
