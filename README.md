# NER Smart Logistics AI — ML Starter

Beginner-friendly SIH MVP for **AI-Based Smart Logistics and Accessibility Intelligence Platform for NER**.

## MVP
- ETA prediction with Random Forest Regression
- Route risk prediction: Low / Medium / High
- Streamlit demo dashboard
- FastAPI `/predict` endpoint

**Important:** `data/routes.csv` is synthetic demo data. It is for learning/prototyping, not real-world NER accuracy.

## Setup (Windows / VS Code)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python ml/train.py
streamlit run demo/app.py
```

API:
```bash
uvicorn api.main:app --reload
```
Then open `http://127.0.0.1:8000/docs` in a browser.

## ML workflow
```text
CSV → Pandas → features/target → train/test split
→ Random Forest → prediction → MAE/R² or Accuracy/F1
→ saved .joblib model → API/Dashboard
```

Features:
`distance_km, elevation_m, slope_pct, rainfall_mm, road_quality, traffic_level, disruption`

Targets:
- ETA: `travel_time_hr`
- Risk: `risk`

## 2-day SIH plan
**Day 1:** run project, understand `train.py`/`predict.py`, connect frontend to API, collect screenshots.

**Day 2:** add real/public NER data if available, add map/route comparison, polish dashboard, clean GitHub, rehearse pitch.

## What to tell judges
“We use route and environmental features such as distance, elevation, slope, rainfall, road quality, traffic and disruptions. A regression model estimates travel time and a classification model estimates route risk. The routing layer can compare candidate routes using ETA and risk instead of only shortest distance.”

Do not claim the synthetic demo dataset represents real NER conditions or production accuracy.
