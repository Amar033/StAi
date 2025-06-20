from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import joblib
import warnings
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

compare_router = APIRouter(prefix="/compare", tags=["compare"])

class CompareRequest(BaseModel):
    tickers: List[str]

def get_project_root():
    """Get the project root directory consistently across all modules"""
    current_file = Path(__file__).resolve()
    
    # For Railway deployment, we need to find the actual project root
    # Try multiple approaches to be safe
    
    # Method 1: Look for main.py in parent directories
    current_dir = current_file.parent
    while current_dir != current_dir.parent:  # Don't go beyond filesystem root
        if (current_dir / "main.py").exists():
            logger.info(f"Found main.py at: {current_dir}")
            return current_dir
        current_dir = current_dir.parent
    
    # Method 2: Use working directory if it contains main.py
    cwd = Path.cwd()
    if (cwd / "main.py").exists():
        logger.info(f"Using current working directory: {cwd}")
        return cwd
    
    # Method 3: Go up from current file location (fallback)
    # backend/routers/compare.py -> backend/routers -> backend -> project_root
    fallback_root = current_file.parent.parent.parent
    logger.info(f"Using fallback project root: {fallback_root}")
    return fallback_root

def get_model_paths(ticker: str):
    """Get consistent model paths for all modules"""
    project_root = get_project_root()
    models_dir = project_root / "models"
    
    model_filename = f"{ticker}_xg.pkl"
    scaler_filename = f"{ticker}_scaler.pkl"
    
    model_path = models_dir / model_filename
    scaler_path = models_dir / scaler_filename
    
    logger.info(f"Model paths for {ticker}:")
    logger.info(f"  Models dir: {models_dir}")
    logger.info(f"  Model: {model_path}")
    logger.info(f"  Scaler: {scaler_path}")
    logger.info(f"  Model exists: {model_path.exists()}")
    logger.info(f"  Scaler exists: {scaler_path.exists()}")
    
    return str(model_path), str(scaler_path)

def load_model_and_scaler(symbol: str):
    """Load model and scaler with consistent error handling"""
    try:
        model_path, scaler_path = get_model_paths(symbol)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
            
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            logger.info(f"✅ Successfully loaded model and scaler for {symbol}")
            return model, scaler
            
    except Exception as e:
        logger.error(f"❌ Error loading model for {symbol}: {str(e)}")
        raise

def get_stock_features(ticker: str):
    """Extract stock features for prediction"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        
        if hist.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        latest_data = hist.iloc[-1]
        
        # Basic OHLCV features
        high = float(latest_data['High'])
        low = float(latest_data['Low'])
        open_price = float(latest_data['Open'])
        volume = float(latest_data['Volume'])
        
        # Moving averages
        ma10 = float(hist['Close'].rolling(window=10).mean().iloc[-1])
        ma50 = float(hist['Close'].rolling(window=50).mean().iloc[-1])
        
        # Returns calculation
        if len(hist) > 1:
            prev_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            returns = float((current_close - prev_close) / prev_close)
        else:
            returns = 0.0
        
        # Volatility calculation
        daily_returns = hist['Close'].pct_change().dropna()
        if len(daily_returns) >= 20:
            volatility = float(daily_returns.rolling(window=20).std().iloc[-1])
        else:
            volatility = float(daily_returns.std()) if len(daily_returns) > 0 else 0.02
        
        # Handle NaN values
        if pd.isna(ma50):
            ma50 = ma10
        if pd.isna(volatility):
            volatility = 0.02
        
        features = [open_price, high, low, volume, ma10, ma50, returns, volatility]
        
        return features, hist
        
    except Exception as e:
        logger.error(f"Error extracting features for {ticker}: {str(e)}")
        raise ValueError(f"Error extracting features for {ticker}: {str(e)}")

def get_stock_basic_info(ticker: str):
    """Get basic stock information"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if hist.empty:
            return {
                "symbol": ticker.upper(),
                "name": ticker.upper(),
                "price": "N/A",
                "change": "N/A",
                "volume": "N/A",
                "current_close": 0
            }
            
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

def predict_single_stock(symbol: str):
    """Predict price for a single stock"""
    try:
        symbol = symbol.upper()
        logger.info(f"Predicting for {symbol}")
        
        # Get features and basic info
        features, hist_data = get_stock_features(symbol)
        basic_info = get_stock_basic_info(symbol)
        
        # Load model and scaler
        model, scaler = load_model_and_scaler(symbol)
        
        # Create DataFrame with proper feature names
        feature_names = ['Open', 'High', 'Low', 'Volume', 'MA10', 'MA50', 'Returns', 'Volatility']
        features_df = pd.DataFrame([features], columns=feature_names)
        
        # Scale features and predict
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            features_scaled = scaler.transform(features_df)
            predicted_close = model.predict(features_scaled)
        
        # Calculate metrics
        current_close = basic_info["current_close"]
        prediction_value = float(predicted_close[0])
        
        if current_close > 0:
            change_amount = prediction_value - current_close
            change_percent = (change_amount / current_close) * 100
            prediction_diff = abs(change_amount) / current_close
            confidence = max(60, min(95, 90 - (prediction_diff * 100)))
        else:
            change_amount = 0
            change_percent = 0
            confidence = 75
        
        # Determine trend
        if prediction_value > current_close * 1.02:
            trend = "Bullish"
        elif prediction_value < current_close * 0.98:
            trend = "Bearish"
        else:
            trend = "Neutral"
        
        # Calculate risk level
        recent_return = features[6]  # Returns feature
        volatility = features[7]     # Volatility feature
        
        if volatility > 0.05 or abs(recent_return) > 0.03:
            risk_level = "High"
        elif volatility > 0.02 or abs(recent_return) > 0.01:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "symbol": basic_info["symbol"],
            "name": basic_info["name"],
            "current_price": basic_info["price"],
            "current_change": basic_info["change"],
            "volume": basic_info["volume"],
            "predicted_price": f"{prediction_value:.2f}",
            "predicted_change": f"{change_amount:+.2f} ({change_percent:+.2f}%)",
            "confidence": f"{confidence:.0f}%",
            "trend": trend,
            "risk_level": risk_level,
            "volatility": f"{volatility:.4f}",
            "recent_return": f"{recent_return:.4f}",
            "success": True
        }
        
    except FileNotFoundError as e:
        logger.error(f"❌ Model not found for {symbol}: {str(e)}")
        return {
            "symbol": symbol,
            "name": symbol,
            "error": f"Prediction model not available for {symbol}",
            "success": False
        }
    except Exception as e:
        logger.error(f"❌ Error predicting {symbol}: {str(e)}")
        return {
            "symbol": symbol,
            "name": symbol,
            "error": f"Prediction failed: {str(e)}",
            "success": False
        }

def calculate_portfolio_metrics(predictions: List[Dict[str, Any]]):
    """Calculate portfolio-level metrics"""
    try:
        successful_predictions = [p for p in predictions if p.get("success", False)]
        
        if not successful_predictions:
            return {
                "total_symbols": len(predictions),
                "successful_predictions": 0,
                "failed_predictions": len(predictions),
                "average_confidence": "N/A",
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0
            }
        
        # Extract confidence values (remove % and convert to float)
        confidences = []
        for pred in successful_predictions:
            conf_str = pred.get("confidence", "0%")
            try:
                conf_value = float(conf_str.replace("%", ""))
                confidences.append(conf_value)
            except:
                pass
        
        avg_confidence = np.mean(confidences) if confidences else 0
        
        # Count trends
        trends = [p.get("trend", "Unknown") for p in successful_predictions]
        bullish_count = trends.count("Bullish")
        bearish_count = trends.count("Bearish")
        neutral_count = trends.count("Neutral")
        
        # Count risk levels
        risk_levels = [p.get("risk_level", "Unknown") for p in successful_predictions]
        high_risk_count = risk_levels.count("High")
        medium_risk_count = risk_levels.count("Medium")
        low_risk_count = risk_levels.count("Low")
        
        return {
            "total_symbols": len(predictions),
            "successful_predictions": len(successful_predictions),
            "failed_predictions": len(predictions) - len(successful_predictions),
            "average_confidence": f"{avg_confidence:.1f}%",
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count
        }
        
    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {str(e)}")
        return {
            "total_symbols": len(predictions),
            "error": f"Error calculating metrics: {str(e)}"
        }

@compare_router.post("/")
def compare_stocks(request: CompareRequest):
    """Compare multiple stocks with predictions and analysis"""
    try:
        if not request.tickers:
            raise HTTPException(status_code=400, detail="No tickers provided")
        
        if len(request.tickers) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 tickers allowed")
        
        logger.info(f"Comparing stocks: {request.tickers}")
        
        # Get predictions for all tickers
        predictions = []
        for ticker in request.tickers:
            try:
                prediction = predict_single_stock(ticker.strip().upper())
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")
                predictions.append({
                    "symbol": ticker.upper(),
                    "name": ticker.upper(),
                    "error": f"Processing failed: {str(e)}",
                    "success": False
                })
        
        # Calculate portfolio metrics
        portfolio_metrics = calculate_portfolio_metrics(predictions)
        
        # Sort predictions by success first, then by confidence
        def sort_key(pred):
            if not pred.get("success", False):
                return (0, 0)  # Failed predictions go last
            try:
                conf_str = pred.get("confidence", "0%")
                conf_value = float(conf_str.replace("%", ""))
                return (1, conf_value)  # Success first, then by confidence
            except:
                return (1, 0)
        
        predictions.sort(key=sort_key, reverse=True)
        
        return {
            "comparison_id": f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "requested_tickers": request.tickers,
            "predictions": predictions,
            "portfolio_metrics": portfolio_metrics,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@compare_router.get("/debug/paths")
def debug_paths():
    """Debug endpoint to check path resolution"""
    try:
        project_root = get_project_root()
        models_dir = project_root / "models"
        
        # List available models
        available_models = []
        if models_dir.exists():
            try:
                pkl_files = [f for f in models_dir.iterdir() if f.suffix == '.pkl']
                available_models = [f.name for f in pkl_files]
            except Exception as e:
                available_models = [f"Error reading directory: {e}"]
        
        return {
            "current_file": str(Path(__file__).resolve()),
            "working_directory": str(Path.cwd()),
            "project_root": str(project_root),
            "models_directory": str(models_dir),
            "models_directory_exists": models_dir.exists(),
            "available_models": available_models[:20],  # Limit output
            "total_models": len(available_models) if isinstance(available_models, list) else 0
        }
    except Exception as e:
        return {"error": str(e)}

@compare_router.get("/health")
def compare_health():
    """Health check for compare router"""
    try:
        project_root = get_project_root()
        models_dir = project_root / "models"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "models_directory_accessible": models_dir.exists(),
            "project_root": str(project_root)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }