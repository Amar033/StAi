from pydantic import BaseModel
from typing import List
from fastapi import APIRouter
import pandas as pd
import joblib

from utils.sentiment import get_sentiment_for_ticker

compare_router =APIRouter()

class CompareRequest(BaseModel):
    tickers: List[str]

@compare_router.post("/compare")
def compare_stocks(req: CompareRequest):
    results=[]
    for ticker in req.tickers:
        try:
            df=pd.read_csv(f"../data/processed/{ticker}_processed.csv")
            latest_features=df.drop(columns=["Date","Close"]).iloc[-1].values.reshape(1,-1)

            model=joblib.load(f"../models/{ticker}_linear.pkl")
            scaler_path = f"../models/{ticker}_scaler.pkl"
            scaler=joblib.load(scaler_path)
            features_scaled = scaler.transform(latest_features)

            prediction = float(model.predict(features_scaled))
            latest_price = df["Close"].iloc[-1]
            sentiment = get_sentiment_for_ticker(ticker)
            results.append({
                "ticker": ticker,
                "latest_price": round(float(latest_price), 2),
                "predicted_price": round(float(prediction), 2),
                "sentiment": sentiment
            })
        except Exception as e:
            results.append({
                "ticker":ticker,
                "error":str(e)
            })
    return results