# MedChain — Medical Blockchain Web App

## Quick Start

```bash
# Install Flask (only dependency)
pip install flask

# Start the server
python app.py
```

Then open in any browser on your network:
- Same machine: http://localhost:5000
- Other machines: http://<server-ip>:5000

## Files

```
medchain_webapp/
├── app.py          ← Flask REST API server (run this)
├── blockchain.py   ← Core blockchain logic (unchanged)
└── static/
    └── index.html  ← Full web frontend (auto-served)
```

## How Multiple Systems Connect

The server binds to `0.0.0.0:5000`, meaning every machine on your
local network can open a browser and connect to the same shared
blockchain state. Each browser tab is an independent "node" that
selects its role (Diagnostic Center, Doctor, Pharmacy, Ledger).

## REST API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/patients | Register new patient |
| GET  | /api/patients | List all patients |
| GET  | /api/patients/:id | Get single patient |
| POST | /api/test-reports | Add test report |
| POST | /api/symptoms | Update symptoms |
| POST | /api/prescriptions | Add prescription |
| GET  | /api/prescriptions/:id | Get prescriptions |
| GET  | /api/chain | Full blockchain |
| GET  | /api/transactions | All transactions |
| GET  | /api/wallets | Wallet balances |
| GET  | /api/validate | Chain integrity |
| GET  | /api/stats | Summary stats |
