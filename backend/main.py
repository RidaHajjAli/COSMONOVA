from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import Optional, List, Dict
import numpy as np
import io
from catboost import CatBoostClassifier

app = FastAPI(title="Stellar Signal API", version="1.0.0")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the dataset and model
DATA_PATH = "backend/data/results.csv"
MODEL_PATH = "ml-pipeline/model/catboost_model.cbm"
df = None
model = None
feature_columns = None
cat_features = []

def load_data():
    global df
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✅ Loaded {len(df)} records from {DATA_PATH}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        df = pd.DataFrame()

def load_model():
    global model, feature_columns, cat_features
    try:
        model = CatBoostClassifier()
        model.load_model(MODEL_PATH)
        
        # Get feature names used in training
        try:
            feature_columns = model.feature_names_
            print(f"✅ Model loaded with {len(feature_columns)} features")
        except AttributeError:
            print("⚠️ Model does not have stored feature names")
            feature_columns = []
        
        # Get categorical feature names
        cat_features = model.get_param('cat_features')
        if cat_features is None:
            cat_features = []
        
        print(f"✅ Loaded model from {MODEL_PATH}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        model = None

def prepare_input(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares any DataFrame to feed the trained CatBoost model:
    - Keeps only training features
    - Reorders columns
    - Fills missing features with 0
    - Converts categorical features to strings
    """
    if feature_columns is None or len(feature_columns) == 0:
        return df_input
    
    # Keep only features that the model expects
    df_prepared = df_input.reindex(columns=feature_columns, fill_value=0)
    
    # Convert categorical features to string type
    for col in cat_features:
        if col in df_prepared.columns:
            df_prepared[col] = df_prepared[col].astype(str)
    
    return df_prepared

@app.on_event("startup")
async def startup_event():
    load_data()
    load_model()

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

class SimulatedPlanetData(BaseModel):
    koi_period: float
    koi_time0bk: float
    koi_impact: float
    koi_duration: float
    koi_depth: float
    koi_prad: float
    koi_model_snr: float
    koi_steff: float
    koi_slogg: float
    koi_srad: float
    koi_kepmag: float

class PredictionResult(BaseModel):
    prediction: str
    probability_false_positive: float
    probability_candidate: float
    confidence_level: str
    is_confirmed: bool
    input_data: Dict

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Stellar Signal API",
        "status": "online",
        "total_planets": len(df) if df is not None else 0,
        "model_loaded": model is not None
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "data_loaded": df is not None and not df.empty,
        "records": len(df) if df is not None else 0,
        "model_loaded": model is not None,
        "features": len(feature_columns) if feature_columns else 0
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
    
    # Determine if confirmed based on probability threshold (>0.5)
    is_confirmed = prob > 0.5
    
    return PlanetResult(
        id=int(planet['id']),
        name=str(planet['name']),
        predicted_disposition=str(planet['predicted_disposition']),
        probability_confirmed=prob,
        is_confirmed=is_confirmed,
        confidence_level=confidence
    )

@app.post("/predict", response_model=PredictionResult)
async def predict_planet(data: SimulatedPlanetData):
    """
    Predict if a planet is a candidate or false positive based on input parameters
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Convert input data to DataFrame
        input_dict = data.dict()
        df_input = pd.DataFrame([input_dict])
        
        # Prepare the data for the model
        df_prepared = prepare_input(df_input)
        
        # Get prediction and probabilities
        prediction = model.predict(df_prepared)[0]
        probabilities = model.predict_proba(df_prepared)[0]
        
        # CatBoost typically returns [prob_class_0, prob_class_1]
        # Assuming class 0 = FALSE POSITIVE, class 1 = CANDIDATE
        prob_false_positive = float(probabilities[0])
        prob_candidate = float(probabilities[1])
        
        # Determine predicted disposition
        predicted_disposition = "CANDIDATE" if prediction == 1 else "FALSE POSITIVE"
        
        # Determine confidence level
        if prob_candidate >= 0.8:
            confidence = "High"
        elif prob_candidate >= 0.5:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        # Determine if confirmed
        is_confirmed = prob_candidate > 0.5
        
        return PredictionResult(
            prediction=predicted_disposition,
            probability_false_positive=prob_false_positive,
            probability_candidate=prob_candidate,
            confidence_level=confidence,
            is_confirmed=is_confirmed,
            input_data=input_dict
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict_csv")
async def predict_from_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file and get predictions for all rows
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Read the uploaded CSV file
        contents = await file.read()
        df_input = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Prepare the data for the model
        df_prepared = prepare_input(df_input)
        
        # Get predictions and probabilities
        predictions = model.predict(df_prepared)
        probabilities = model.predict_proba(df_prepared)
        
        # Add results to DataFrame
        df_input['prediction'] = ['CANDIDATE' if p == 1 else 'FALSE POSITIVE' for p in predictions]
        df_input['probability_false_positive'] = probabilities[:, 0].astype(float)
        df_input['probability_candidate'] = probabilities[:, 1].astype(float)
        df_input['is_confirmed'] = (probabilities[:, 1] > 0.5).astype(bool)
        
        # Convert to native Python types for JSON serialization
        results = []
        for _, row in df_input.iterrows():
            row_dict = {}
            for col, val in row.items():
                if pd.isna(val):
                    row_dict[col] = None
                elif isinstance(val, (np.integer, np.int64, np.int32)):
                    row_dict[col] = int(val)
                elif isinstance(val, (np.floating, np.float64, np.float32)):
                    row_dict[col] = float(val)
                elif isinstance(val, (np.bool_, bool)):
                    row_dict[col] = bool(val)
                else:
                    row_dict[col] = val
            results.append(row_dict)
        
        return {
            "total_rows": int(len(results)),
            "confirmed_count": int(sum(probabilities[:, 1] > 0.5)),
            "false_positive_count": int(sum(probabilities[:, 1] <= 0.5)),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV prediction error: {str(e)}")

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
    
    # Count based on probability threshold (>0.5 = confirmed candidate)
    confirmed = len(df[df['probability_confirmed'] > 0.5])
    false_positive = len(df[df['probability_confirmed'] <= 0.5])
    avg_probability = df['probability_confirmed'].mean()
    
    # Also count by disposition string (for reference)
    disposition_candidates = len(df[df['predicted_disposition'].str.upper() == 'CANDIDATE'])
    disposition_false_positives = len(df[df['predicted_disposition'].str.upper() == 'FALSE POSITIVE'])
    
    return {
        "total_objects": len(df),
        "confirmed_candidates": confirmed,
        "false_positives": false_positive,
        "average_probability": round(avg_probability, 4),
        "high_confidence": len(df[df['probability_confirmed'] >= 0.8]),
        "medium_confidence": len(df[(df['probability_confirmed'] >= 0.5) & (df['probability_confirmed'] < 0.8)]),
        "low_confidence": len(df[df['probability_confirmed'] < 0.5]),
        "disposition_stats": {
            "candidates": disposition_candidates,
            "false_positives": disposition_false_positives
        }
    }

@app.get("/model/info")
async def get_model_info():
    """
    Get information about the loaded model
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    return {
        "model_loaded": True,
        "feature_count": len(feature_columns) if feature_columns else 0,
        "features": feature_columns if feature_columns else [],
        "categorical_features": cat_features,
        "model_path": MODEL_PATH
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)