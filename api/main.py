from fastapi import FastAPI
from pydantic import BaseModel, Field
from ml.predict import predict_route

app=FastAPI(title="NER Smart Logistics AI API",version="0.1")

class RouteInput(BaseModel):
    distance_km: float=Field(gt=0,le=1000)
    elevation_m: float=Field(ge=0,le=5000)
    slope_pct: float=Field(ge=0,le=40)
    rainfall_mm: float=Field(ge=0,le=500)
    road_quality: int=Field(ge=1,le=5)
    traffic_level: int=Field(ge=1,le=5)
    disruption: int=Field(ge=0,le=1)

@app.get("/")
def root(): return {"message":"NER Smart Logistics AI API is running","docs":"/docs"}

@app.post("/predict")
def predict(data: RouteInput): return predict_route(**data.model_dump())
