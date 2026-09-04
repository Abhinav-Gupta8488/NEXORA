from pathlib import Path
import json, joblib, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/routes.csv"; OUT=ROOT/"ml/models"; OUT.mkdir(exist_ok=True)
F=["distance_km","elevation_m","slope_pct","rainfall_mm","road_quality","traffic_level","disruption"]
df=pd.read_csv(DATA); X=df[F]

Xa,Xb,ya,yb=train_test_split(X,df.travel_time_hr,test_size=.2,random_state=42)
eta=RandomForestRegressor(n_estimators=250,max_depth=12,random_state=42,n_jobs=-1).fit(Xa,ya)
ep=eta.predict(Xb)

Xa,Xb,ya,yb=train_test_split(X,df.risk,test_size=.2,random_state=42,stratify=df.risk)
risk=RandomForestClassifier(n_estimators=250,max_depth=12,class_weight="balanced",random_state=42,n_jobs=-1).fit(Xa,ya)
rp=risk.predict(Xb)

metrics={"eta":{"MAE_hours":round(mean_absolute_error(yb if False else train_test_split(X,df.travel_time_hr,test_size=.2,random_state=42)[3],ep),4),
"R2":round(r2_score(train_test_split(X,df.travel_time_hr,test_size=.2,random_state=42)[3],ep),4)},
"risk":{"accuracy":round(accuracy_score(yb,rp),4),"f1_weighted":round(f1_score(yb,rp,average="weighted"),4)}}
joblib.dump(eta,OUT/"eta_model.joblib"); joblib.dump(risk,OUT/"risk_model.joblib")
(OUT/"metrics.json").write_text(json.dumps(metrics,indent=2))
print(metrics)
