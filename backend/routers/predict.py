from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class PredictRequest(BaseModel):
    ticker: str
    features: list

def get_stock_features(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        if hist.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        latest_data = hist.iloc[-1]
        high = latest_data['High']
        low = latest_data['Low']
        open_price = latest_data['Open']
        volume = latest_data['Volume']

        ma10 = hist['Close'].rolling(window=10).mean().iloc[-1]
        ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        if len(hist) > 1:
            prev_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            returns = (current_close - prev_close) / prev_close
        else:
            returns = 0.0
        
        daily_returns = hist['Close'].pct_change().dropna()
        if len(daily_returns) >= 20:
            volatility = daily_returns.rolling(window=20).std().iloc[-1]
        else:
            volatility = daily_returns.std()
        
        if pd.isna(ma50):
            ma50 = ma10
        if pd.isna(volatility):
            volatility = 0.02
        
        features = [
            float(open_price),  # Open - first in training order
            float(high),        # High - second in training order
            float(low),         # Low - third in training order
            float(volume),      # Volume - fourth in training order
            float(ma10),        # MA10 - fifth in training order
            float(ma50),        # MA50 - sixth in training order
            float(returns),     # Returns - seventh in training order
            float(volatility)   # Volatility - eighth in training order
        ]
        
        return features, hist
        
    except Exception as e:
        logger.error(f"Error extracting features for {ticker}: {str(e)}")
        raise ValueError(f"Error extracting features for {ticker}: {str(e)}")

def get_stock_basic_info(ticker: str):
    """Get basic stock information for display"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if hist.empty:
            raise ValueError(f"No historical data available for {ticker}")
            
        info = stock.info
        
        current_close = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_close
        change = current_close - prev_close
        change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
        
        return {
            "symbol": ticker.upper(),
            "name": info.get("longName", ticker.upper()),
            "price": f"{current_close:.2f}",
            "change": f"{change:+.2f} ({change_percent:+.2f}%)",
            "volume": f"{hist['Volume'].iloc[-1]:,.0f}",
            "current_close": current_close
        }
    except Exception as e:
        logger.error(f"Error getting basic info for {ticker}: {str(e)}")
        return {
            "symbol": ticker.upper(),
            "name": ticker.upper(),
            "price": "N/A",
            "change": "N/A",
            "volume": "N/A",
            "current_close": 0
        }

@router.get("/predict/{symbol}")
def predict_stock_price(symbol: str):
    """
    Predict next Close price for a given symbol using:
    High, Low, Open, Volume, MA10, MA50, Returns, Volatility
    """
    try:
        symbol = symbol.upper()
        logger.info(f"Processing prediction request for {symbol}")
        
        # Get features and basic info
        features, hist_data = get_stock_features(symbol)
        basic_info = get_stock_basic_info(symbol)
        
        # Load model and scaler
        model_path = f"..\\models\\{symbol}_xg.pkl"
        scaler_path = f"..\\models\\{symbol}_scaler.pkl"
        
        logger.info(f"Loading model from: {model_path}")
        logger.info(f"Loading scaler from: {scaler_path}")
        
        # Suppress sklearn warnings temporarily
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
            
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
        
        # Define feature names matching EXACT order from training
        feature_names = ['Open', 'High', 'Low', 'Volume', 'MA10', 'MA50', 'Returns', 'Volatility']
        
        # Create DataFrame with proper feature names to avoid sklearn warning
        features_df = pd.DataFrame([features], columns=feature_names)
        
        # Scale features
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            features_scaled = scaler.transform(features_df)
        
        # Make prediction
        predicted_close = model.predict(features_scaled)
        
        # Calculate confidence and trend
        current_close = basic_info["current_close"]
        if current_close > 0:
            prediction_diff = abs(predicted_close[0] - current_close) / current_close
            confidence = max(60, min(95, 90 - (prediction_diff * 100)))
        else:
            confidence = 75  # Default confidence if current_close is invalid
            
        if predicted_close[0] > current_close * 1.02:  # >2% increase
            trend = "Bullish"
        elif predicted_close[0] < current_close * 0.98:  # >2% decrease
            trend = "Bearish"
        else:
            trend = "Neutral"
        
        # Calculate sentiment
        recent_return = features[6]
        if recent_return > 0.01:
            sentiment_score = "Positive"
        elif recent_return < -0.01:
            sentiment_score = "Negative"
        else:
            sentiment_score = "Neutral"
        
        logger.info(f"Prediction successful for {symbol}: {predicted_close[0]:.2f}")
        
        return {
            "symbol": basic_info["symbol"],
            "name": basic_info["name"],
            "price": basic_info["price"],
            "change": basic_info["change"],
            "volume": basic_info["volume"],
            "prediction": f"{predicted_close[0]:.2f}",
            "confidence": f"{confidence:.0f}%",
            "trend": trend,
            "sentimentScore": sentiment_score,
            "success": True,
            "features_used": {
                "open": features[0],    # Open
                "high": features[1],    # High  
                "low": features[2],     # Low
                "volume": features[3],  # Volume
                "ma10": features[4],    # MA10
                "ma50": features[5],    # MA50
                "returns": features[6], # Returns
                "volatility": features[7] # Volatility
            }
        }
        
    except FileNotFoundError as e:
        logger.error(f"Model files not found for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=404, 
            detail=f"Model or scaler for {symbol} not found. Make sure both {symbol}_xg.pkl and {symbol}_scaler.pkl exist in the models directory."
        )
    except ValueError as e:
        logger.error(f"ValueError for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/predict")
def predict_price_with_features(data: PredictRequest):
    """
    Original endpoint for manual feature input
    Expects features in order: [High, Low, Open, Volume, MA10, MA50, Returns, Volatility]
    """
    try:
        if len(data.features) != 8:
            raise HTTPException(
                status_code=400, 
                detail="Expected 8 features: [High, Low, Open, Volume, MA10, MA50, Returns, Volatility]"
            )
        
        model_path = f"..\\models\\{data.ticker}_xg.pkl"
        scaler_path = f"..\\models\\{data.ticker}_scaler.pkl"
        
        # Suppress sklearn warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
            
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
        
        # Create DataFrame with proper feature names matching training data
        feature_names = ['Open', 'High', 'Low', 'Volume', 'MA10', 'MA50', 'Returns', 'Volatility']
        features_df = pd.DataFrame([data.features], columns=feature_names)
        
        # Scale and predict
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            features_scaled = scaler.transform(features_df)
            
        prediction = model.predict(features_scaled)
        
        return {
            "ticker": data.ticker, 
            "predicted_close": float(prediction[0]),
            "features_used": {
                "open": data.features[0],    # Open
                "high": data.features[1],    # High
                "low": data.features[2],     # Low
                "volume": data.features[3],  # Volume
                "ma10": data.features[4],    # MA10
                "ma50": data.features[5],    # MA50
                "returns": data.features[6], # Returns
                "volatility": data.features[7] # Volatility
            }
        }
        
    except FileNotFoundError as e:
        logger.error(f"Model files not found for {data.ticker}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Model or scaler for {data.ticker} not found. Make sure both {data.ticker}_xg.pkl and {data.ticker}_scaler.pkl exist in the models directory."
        )
    except Exception as e:
        logger.error(f"Prediction error for {data.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/price-history/{symbol}")
def get_price_history(symbol: str, range: int = 60):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=f"{range}d")
        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data found.")

        price_data = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "price": round(row["Close"], 2)
            }
            for date, row in hist.iterrows()
        ]

        return {"symbol": symbol.upper(), "history": price_data}

    except Exception as e:
        logger.error(f"Error fetching price history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching historical data.")
