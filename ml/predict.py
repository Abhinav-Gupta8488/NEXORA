from pathlib import Path
import joblib, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; M=ROOT/"ml/models"
F=["distance_km","elevation_m","slope_pct","rainfall_mm","road_quality","traffic_level","disruption"]
eta=joblib.load(M/"eta_model.joblib"); risk=joblib.load(M/"risk_model.joblib")

def predict_route(**kwargs):
    row=pd.DataFrame([{k:kwargs[k] for k in F}])[F]
    hours=float(eta.predict(row)[0]); r=str(risk.predict(row)[0])
    conf=float(max(risk.predict_proba(row)[0]))
    return {"eta_hours":round(max(.05,hours),2),"eta_minutes":round(max(3,hours*60)),
            "risk":r,"confidence":round(conf,3)}
