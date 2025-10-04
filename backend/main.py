from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import Optional
import os

app = FastAPI(title="Stellar Signal API", version="1.0.0")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the dataset
DATA_PATH = "data/results.csv"
df = None

def load_data():
    global df
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✅ Loaded {len(df)} records from {DATA_PATH}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        df = pd.DataFrame()

@app.on_event("startup")
async def startup_event():
    load_data()

# Request/Response Models
class PlanetQuery(BaseModel):
    query: str  # Can be ID or name

class PlanetResult(BaseModel):
    id: int
    name: str
    predicted_disposition: str
    probability_confirmed: float
    is_confirmed: bool
    confidence_level: str

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Stellar Signal API",
        "status": "online",
        "total_planets": len(df) if df is not None else 0
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "data_loaded": df is not None and not df.empty,
        "records": len(df) if df is not None else 0
    }

@app.post("/detect", response_model=PlanetResult)
async def detect_planet(query: PlanetQuery):
    """
    Detect planet by ID or name and return prediction results
    """
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    search_query = query.query.strip()
    
    # Try to find by ID first (if numeric)
    result = None
    if search_query.isdigit():
        result = df[df['id'] == int(search_query)]
    
    # If not found by ID, search by name (case-insensitive)
    if result is None or result.empty:
        result = df[df['name'].str.upper() == search_query.upper()]
    
    # If still not found, try partial match
    if result is None or result.empty:
        result = df[df['name'].str.contains(search_query, case=False, na=False)]
    
    if result.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Planet '{search_query}' not found. Please check the ID or name."
        )
    
    # Get the first match
    planet = result.iloc[0]
    
    # Determine confidence level
    prob = float(planet['probability_confirmed'])
    if prob >= 0.8:
        confidence = "High"
    elif prob >= 0.5:
        confidence = "Medium"
    else:
        confidence = "Low"
    
    # Determine if confirmed (typically >0.5 threshold)
    is_confirmed = planet['predicted_disposition'].upper() == 'CANDIDATE' or prob > 0.5
    
    return PlanetResult(
        id=int(planet['id']),
        name=str(planet['name']),
        predicted_disposition=str(planet['predicted_disposition']),
        probability_confirmed=prob,
        is_confirmed=is_confirmed,
        confidence_level=confidence
    )

@app.get("/planets/list")
async def list_planets(limit: int = 100, offset: int = 0):
    """
    List available planets with pagination
    """
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    total = len(df)
    planets = df.iloc[offset:offset+limit][['id', 'name', 'predicted_disposition']].to_dict('records')
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "planets": planets
    }

@app.get("/stats")
async def get_statistics():
    """
    Get dataset statistics
    """
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    confirmed = len(df[df['predicted_disposition'].str.upper() == 'CANDIDATE'])
    false_positive = len(df[df['predicted_disposition'].str.upper() == 'FALSE POSITIVE'])
    avg_probability = df['probability_confirmed'].mean()
    
    return {
        "total_objects": len(df),
        "confirmed_candidates": confirmed,
        "false_positives": false_positive,
        "average_probability": round(avg_probability, 4),
        "high_confidence": len(df[df['probability_confirmed'] >= 0.8]),
        "medium_confidence": len(df[(df['probability_confirmed'] >= 0.5) & (df['probability_confirmed'] < 0.8)]),
        "low_confidence": len(df[df['probability_confirmed'] < 0.5])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)