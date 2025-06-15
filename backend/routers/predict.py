from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

router=APIRouter()

class PredictRequest(BaseModel):
    ticker: str
    features: list

# @router.post("/predict")
# def predict_price(data: PredictRequest):
#     try:
#         model_path = f"..\models\{data.ticker}_xg.pkl"
#         with open(model_path, "rb") as f:
#             model = joblib.load(f)
#         scaler=StandardScaler()
        
#         features = np.array(data.features).reshape(1, -1)
#         # input_scaled=scaler.transform(features)
#         # input_scaled = scaler.transform([features])
#         prediction = model.predict(features)
#         return {"ticker": data.ticker, "predicted_price": float(prediction[0])}
#     except FileNotFoundError:
#         return {"error": f"Model for {data.ticker} not found."}
#     except Exception as e:
#         return {"error": str(e)}





@router.post("/predict")
def predict_price(data: PredictRequest):
    try:
        # Load both model and scaler
        model_path = f"..\\models\\{data.ticker}_xg.pkl"
        scaler_path = f"..\\models\\{data.ticker}_scaler.pkl"
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare and scale features
        features = np.array(data.features).reshape(1, -1)
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)
        
        return {"ticker": data.ticker, "predicted_price": float(prediction[0])}
        
    except FileNotFoundError as e:
        return {"error": f"Model or scaler for {data.ticker} not found. Make sure both {data.ticker}_xg.pkl and {data.ticker}_scaler.pkl exist."}
    except Exception as e:
        return {"error": f"Prediction error: {str(e)}"}