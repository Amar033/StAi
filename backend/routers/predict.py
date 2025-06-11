from fastapi import APIRouter
from pydantic import BaseModel
import pickle
import numpy as np

router=APIRouter()

class PredictRequest(BaseModel):
    ticker: str
    features: list

@router.post("/predict")
def predict_price(data: PredictRequest):
    try:
        model_path = f"..\models\{data.ticker}_linear.pkl"
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        features = np.array(data.features).reshape(1, -1)
        prediction = model.predict(features)
        return {"ticker": data.ticker, "predicted_price": prediction[0]}
    except FileNotFoundError:
        return {"error": f"Model for {data.ticker} not found."}
    except Exception as e:
        return {"error": str(e)}