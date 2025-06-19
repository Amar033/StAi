from fastapi import FastAPI
from routers import predict
from utils.constants import TICKER_LIST
from fastapi import HTTPException
from utils.features import get_features_for_ticker
from utils.sentiment import get_sentiment_for_ticker
from pydantic import BaseModel
from typing import List
from routers import compare
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import date
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from routers import insights



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompareRequest(BaseModel):
    tickers: List[str]

app = FastAPI(title="StAI- Stock Prediction API",
            description="Predict Stock Prices",
            version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001","http://localhost:5173","https://st-ai.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)

@app.get("/")
async def root():
    return {"message":"StAI - Stock Prediction made easy"}

@app.get("/tickers")
def get_supported_tickers():
    return {"tickers": TICKER_LIST}

@app.get("/features/{ticker}")
def get_features(ticker: str):
    features=get_features_for_ticker(ticker)
    if features is None:
        raise HTTPException(status_code=404, detail="Ticker data not found")
    return {"ticker": ticker, "features": features}

@app.get("/sentiment/{ticker}")
def sentiment(ticker:str):
    result=get_sentiment_for_ticker(ticker)
    if not result['articles']:
        raise HTTPException(status_code=404, detail="No news found for ticker")
    return result

# @app.get("/compare")
# def compare_ticker(req: CompareRequest):

app.include_router(compare.compare_router)


app.include_router(insights.insights_router)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
