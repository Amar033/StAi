from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class PredictRequest(BaseModel):
    ticker: str
    features: list

def get_project_root():
    """Get the project root directory - handles both local and Railway deployment"""
    current_file = Path(__file__).resolve()
    
    # Check if we're in Railway deployment (frontend is root)
    # In Railway: frontend/backend/routers/predict.py
    # In Local: backend/routers/predict.py
    
    # From backend/routers/predict.py, go up levels to find project root
    potential_roots = [
        current_file.parent.parent.parent,  # For Railway: frontend/backend/routers -> frontend/backend -> frontend
        current_file.parent.parent,         # For Local: backend/routers -> backend -> project_root
    ]
    
    logger.info(f"Current file: {current_file}")
    
    # Try to find the correct root by looking for models directory
    for root in potential_roots:
        models_dir = root / "models"
        if models_dir.exists():
            logger.info(f"Found models directory at: {models_dir}")
            logger.info(f"Using project root: {root}")
            return root
    
    # If no models directory found, check parent directories more systematically
    current = current_file.parent
    for _ in range(5):  # Check up to 5 levels up
        models_dir = current / "models"
        if models_dir.exists():
            logger.info(f"Found models directory at: {models_dir}")
            logger.info(f"Using project root: {current}")
            return current
        current = current.parent
    
    # Fallback to Railway structure assumption
    railway_root = current_file.parent.parent.parent
    logger.warning(f"Models directory not found, using Railway root assumption: {railway_root}")
    return railway_root

def get_model_paths(ticker: str):
    """Get model and scaler paths for prediction models"""
    
    project_root = get_project_root()
    
    # Try multiple possible locations for models
    possible_model_dirs = [
        project_root / "models",           # Standard location
        project_root / "backend" / "models",  # Alternative location
        project_root.parent / "models",    # Parent directory (for Railway)
    ]
    
    model_filename = f"{ticker}_xg.pkl"
    scaler_filename = f"{ticker}_scaler.pkl"
    
    for models_dir in possible_model_dirs:
        model_path = models_dir / model_filename
        scaler_path = models_dir / scaler_filename
        
        logger.info(f"Checking models directory: {models_dir}")
        logger.info(f"Directory exists: {models_dir.exists()}")
        
        if models_dir.exists():
            logger.info(f"Model file exists: {model_path.exists()}")
            logger.info(f"Scaler file exists: {scaler_path.exists()}")
            
            if model_path.exists() and scaler_path.exists():
                logger.info(f"✅ Found model files in: {models_dir}")
                return str(model_path), str(scaler_path)
    
    # If not found, return the first option for error reporting
    models_dir = possible_model_dirs[0]
    model_path = models_dir / model_filename
    scaler_path = models_dir / scaler_filename
    
    logger.error(f"❌ Model files not found in any location")
    return str(model_path), str(scaler_path)

def get_sentiment_model_paths():
    """Get sentiment model paths (in backend/utils/models folder)"""
    
    current_file = Path(__file__).resolve()
    
    # Try multiple possible locations for sentiment models
    possible_sentiment_dirs = [
        current_file.parent.parent / "utils" / "models",  # Standard: backend/utils/models
        current_file.parent.parent.parent / "backend" / "utils" / "models",  # Railway: frontend/backend/utils/models
    ]
    
    for sentiment_dir in possible_sentiment_dirs:
        logger.info(f"Checking sentiment models directory: {sentiment_dir}")
        logger.info(f"Directory exists: {sentiment_dir.exists()}")
        
        if sentiment_dir.exists():
            try:
                contents = list(sentiment_dir.iterdir())
                logger.info(f"Sentiment models directory contents: {[f.name for f in contents]}")
                return sentiment_dir
            except Exception as e:
                logger.error(f"Could not list sentiment models directory: {e}")
    
    # Return the first option as fallback
    return possible_sentiment_dirs[0]

def debug_directory_structure():
    """Debug function to show the complete directory structure"""
    
    current_file = Path(__file__).resolve()
    project_root = get_project_root()
    
    logger.info("=== COMPLETE DIRECTORY STRUCTURE DEBUG (RAILWAY COMPATIBLE) ===")
    logger.info(f"Current file: {current_file}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Working directory: {Path.cwd()}")
    
    # Check current file's parent directories
    logger.info(f"\n📁 Current file parent structure:")
    current = current_file.parent
    for i in range(5):
        logger.info(f"  Level {i}: {current}")
        if current.exists():
            try:
                contents = [item.name for item in current.iterdir() if item.is_dir()][:5]
                logger.info(f"    Directories: {contents}")
            except:
                pass
        current = current.parent
    
    # Check project root contents
    logger.info(f"\n📁 Project root contents ({project_root}):")
    if project_root.exists():
        try:
            for item in project_root.iterdir():
                item_type = "📁 dir" if item.is_dir() else "📄 file"
                logger.info(f"  {item_type}: {item.name}")
        except Exception as e:
            logger.error(f"Could not list project root: {e}")
    
    # Check for models in multiple locations
    possible_model_locations = [
        project_root / "models",
        project_root / "backend" / "models", 
        project_root.parent / "models",
        project_root / ".." / "models",
    ]
    
    logger.info(f"\n🔍 Checking possible model locations:")
    for location in possible_model_locations:
        try:
            resolved_location = location.resolve()
            exists = resolved_location.exists()
            logger.info(f"  📁 {resolved_location}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
            
            if exists:
                pkl_files = [f for f in resolved_location.iterdir() if f.suffix == '.pkl']
                logger.info(f"    Found {len(pkl_files)} .pkl files")
                if pkl_files:
                    # Show first few files
                    for f in pkl_files[:3]:
                        logger.info(f"      📄 {f.name}")
                    if len(pkl_files) > 3:
                        logger.info(f"      ... and {len(pkl_files) - 3} more")
        except Exception as e:
            logger.error(f"  Error checking {location}: {e}")

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
            float(open_price),  # Open
            float(high),        # High
            float(low),         # Low
            float(volume),      # Volume
            float(ma10),        # MA10
            float(ma50),        # MA50
            float(returns),     # Returns
            float(volatility)   # Volatility
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

def load_model_and_scaler(symbol: str):
    """Load prediction model and scaler - Railway deployment compatible"""
    
    # Debug directory structure in development
    if os.getenv("ENVIRONMENT") != "production":
        debug_directory_structure()
    
    model_path, scaler_path = get_model_paths(symbol)
    
    logger.info(f"Final paths for {symbol}:")
    logger.info(f"  Model: {model_path}")
    logger.info(f"  Scaler: {scaler_path}")
    
    # Check if files exist
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
    
    # Load with warnings suppressed
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
        
        try:
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            logger.info(f"✅ Successfully loaded model and scaler for {symbol}")
            return model, scaler
        except Exception as e:
            logger.error(f"Error loading model files: {str(e)}")
            raise ValueError(f"Error loading model files: {str(e)}")

# DEBUG ENDPOINTS
@router.get("/debug/structure")
def debug_structure():
    """Debug endpoint to show complete directory structure"""
    debug_directory_structure()
    
    project_root = get_project_root()
    current_file = Path(__file__).resolve()
    
    return {
        "current_file": str(current_file),
        "project_root": str(project_root),
        "models_directory": str(project_root / "models"),
        "sentiment_models_directory": str(get_sentiment_model_paths()),
        "working_directory": str(Path.cwd()),
        "environment": {
            "PWD": os.getenv("PWD", "Not set"),
            "PYTHONPATH": os.getenv("PYTHONPATH", "Not set"),
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT", "Not set"),
        }
    }

@router.get("/debug/models")
def debug_models():
    """Debug endpoint to list all available models"""
    project_root = get_project_root()
    
    # Check multiple possible locations
    possible_model_dirs = [
        project_root / "models",
        project_root / "backend" / "models",
        project_root.parent / "models",
    ]
    
    all_models_info = []
    
    for models_dir in possible_model_dirs:
        models_info = {
            "directory": str(models_dir),
            "exists": models_dir.exists(),
            "models": []
        }
        
        if models_dir.exists():
            try:
                pkl_files = [f for f in models_dir.iterdir() if f.suffix == '.pkl']
                models_info["models"] = [f.name for f in pkl_files]
            except Exception as e:
                models_info["error"] = str(e)
        
        all_models_info.append(models_info)
    
    # Check sentiment models
    sentiment_models_dir = get_sentiment_model_paths()
    sentiment_models = []
    if sentiment_models_dir.exists():
        try:
            sentiment_files = list(sentiment_models_dir.iterdir())
            sentiment_models = [f.name for f in sentiment_files]
        except Exception as e:
            sentiment_models = [f"Error reading directory: {e}"]
    
    return {
        "prediction_models_locations": all_models_info,
        "sentiment_models_directory": str(sentiment_models_dir),
        "sentiment_models_exists": sentiment_models_dir.exists(),
        "sentiment_models": sentiment_models
    }

@router.get("/debug/model-check/{symbol}")
def debug_model_check(symbol: str):
    """Check if specific prediction model files exist"""
    symbol = symbol.upper()
    model_path, scaler_path = get_model_paths(symbol)
    
    project_root = get_project_root()
    
    # Check all possible model directories
    possible_model_dirs = [
        project_root / "models",
        project_root / "backend" / "models",
        project_root.parent / "models",
    ]
    
    available_models = []
    for models_dir in possible_model_dirs:
        if models_dir.exists():
            try:
                pkl_files = [f for f in models_dir.iterdir() if f.suffix == '.pkl']
                available_models.extend([f"{models_dir.name}/{f.name}" for f in pkl_files])
            except Exception as e:
                available_models.append(f"Error in {models_dir}: {e}")
    
    return {
        "symbol": symbol,
        "project_root": str(project_root),
        "model_path": model_path,
        "scaler_path": scaler_path,
        "model_exists": os.path.exists(model_path),
        "scaler_exists": os.path.exists(scaler_path),
        "available_models": available_models,
        "expected_files": [f"{symbol}_xg.pkl", f"{symbol}_scaler.pkl"]
    }

# MAIN PREDICTION ENDPOINT
@router.get("/predict/{symbol}")
def predict_stock_price(symbol: str):
    """
    Predict next Close price for a given symbol using:
    Open, High, Low, Volume, MA10, MA50, Returns, Volatility
    """
    try:
        symbol = symbol.upper()
        logger.info(f"Processing prediction request for {symbol}")
        
        # Get features and basic info
        features, hist_data = get_stock_features(symbol)
        basic_info = get_stock_basic_info(symbol)
        
        # Load model and scaler
        model, scaler = load_model_and_scaler(symbol)
        
        # Define feature names matching EXACT order from training
        feature_names = ['Open', 'High', 'Low', 'Volume', 'MA10', 'MA50', 'Returns', 'Volatility']
        
        # Create DataFrame with proper feature names
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
            confidence = 75
            
        if predicted_close[0] > current_close * 1.02:
            trend = "Bullish"
        elif predicted_close[0] < current_close * 0.98:
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
        
        logger.info(f"✅ Prediction successful for {symbol}: {predicted_close[0]:.2f}")
        
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
                "open": features[0],
                "high": features[1],
                "low": features[2],
                "volume": features[3],
                "ma10": features[4],
                "ma50": features[5],
                "returns": features[6],
                "volatility": features[7]
            }
        }
        
    except FileNotFoundError as e:
        logger.error(f"❌ Model files not found for {symbol}: {str(e)}")
        
        project_root = get_project_root()
        
        error_detail = (
            f"Prediction model files for {symbol} not found. "
            f"Expected files: {symbol}_xg.pkl and {symbol}_scaler.pkl. "
            f"Use /debug/models to see available models or /debug/model-check/{symbol} for details."
        )
        
        raise HTTPException(status_code=404, detail=error_detail)
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
    Expects features in order: [Open, High, Low, Volume, MA10, MA50, Returns, Volatility]
    """
    try:
        if len(data.features) != 8:
            raise HTTPException(
                status_code=400, 
                detail="Expected 8 features: [Open, High, Low, Volume, MA10, MA50, Returns, Volatility]"
            )
        
        # Use consistent path handling
        model, scaler = load_model_and_scaler(data.ticker.upper())
        
        # Create DataFrame with proper feature names matching training data
        feature_names = ['Open', 'High', 'Low', 'Volume', 'MA10', 'MA50', 'Returns', 'Volatility']
        features_df = pd.DataFrame([data.features], columns=feature_names)
        
        # Scale and predict
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            features_scaled = scaler.transform(features_df)
            
        prediction = model.predict(features_scaled)
        
        return {
            "ticker": data.ticker.upper(), 
            "predicted_close": float(prediction[0]),
            "features_used": {
                "open": data.features[0],
                "high": data.features[1],
                "low": data.features[2],
                "volume": data.features[3],
                "ma10": data.features[4],
                "ma50": data.features[5],
                "returns": data.features[6],
                "volatility": data.features[7]
            }
        }
        
    except FileNotFoundError as e:
        logger.error(f"Model files not found for {data.ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Model files for {data.ticker} not found.")
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