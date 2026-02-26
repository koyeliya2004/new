# Smart Rooftop Rainwater Harvesting & Groundwater Recharge Assessment System

A full-stack web application that helps citizens estimate rooftop rainwater harvesting (RTRWH) potential and artificial groundwater recharge feasibility at their specific location.

---

## Project Structure

```
.
├── frontend/          # Single-page web application (HTML + CSS + JS)
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── backend/           # Flask REST API
│   ├── app.py
│   ├── requirements.txt
│   └── data/
│       └── rainfall.json
├── docs/
│   └── api.md         # Full API reference
└── README.md
```

---

## Features

| Category | Feature |
|---|---|
| Assessment | Feasibility check, runoff calculation (Roof Area × Rainfall × 0.8) |
| Recommendations | Structure type (pit / trench / shaft), dimensions, cost |
| Data | City-based rainfall lookup, aquifer type, groundwater depth |
| Gamification | Water credit system, neighborhood leaderboard |
| Visualization | Geological digital twin, AR placement preview |
| Utilities | DIY blueprint download, vendor marketplace, policy tracker |
| Accessibility | English, Hindi, Bengali UI languages |

---

## Quick Start (frontend only)

Open `frontend/index.html` directly in a browser.  
All calculations fall back to local JS logic when the backend is offline.

---

## Full Stack Setup

### 1. Backend (Flask API)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API starts on **http://localhost:5000**.

### 2. Frontend

Open `frontend/index.html` in a browser (no build step required).  
When the Flask server is running the app automatically calls the backend APIs
and falls back to local calculations if the server is unavailable.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/calculate` | Runoff & harvested water calculation |
| POST | `/recommend` | Recharge structure recommendation |
| POST | `/cost` | Cost & benefit analysis |
| GET | `/rainfall?city=` | Annual rainfall for a city |
| GET | `/leaderboard` | Community water credit leaderboard |
| GET | `/vendors` | Marketplace vendor listing |

See [`docs/api.md`](docs/api.md) for full request/response schemas.

---

## Runoff Formula

```
Harvested Water (litres) = Roof Area (m²) × Annual Rainfall (mm) × 0.8
```

Runoff coefficient of **0.8** is the CGWB standard value for rooftop surfaces.

---

## Cost Schedule

| Structure | Indicative Cost |
|---|---|
| Recharge pit | ₹5,000 |
| Recharge trench | ₹7,000 |
| Recharge shaft | ₹7,000 |
| Storage tank | ₹10,000 |

---

> Calculations are indicative and based on CGWB guidance. Verify with local engineers before construction.

---

## Deployment on Render

Steps:
1. Push code to GitHub
2. Go to https://render.com
3. Create new Web Service
4. Select repository
5. Set:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
6. Deploy and get live URL
7. Update `BASE_URL` in `frontend/app.js` with your Render service URL

