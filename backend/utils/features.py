import pandas as pd
import os
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_features_for_ticker(ticker: str):
    """Get feature columns for a ticker from processed data"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    path = os.path.join(project_root, "data", "processed", f"{ticker}_processed.csv")
    
    if not os.path.exists(path):
        logger.warning(f"Processed data file not found: {path}")
        return None
        
    try:
        df = pd.read_csv(path)
        excluded_cols = ["Date", "Close", "Target"]
        feature_cols = [col for col in df.columns if col not in excluded_cols]
        logger.info(f"Found {len(feature_cols)} features for {ticker}")
        return feature_cols
    except Exception as e:
        logger.error(f"Error reading processed data for {ticker}: {str(e)}")
        return None

def get_stock_basic_features(ticker: str, period: str = "60d") -> Optional[Dict]:
    """
    Extract basic stock features similar to predict.py
    
    Args:
        ticker: Stock ticker symbol
        period: Period for historical data
        
    Returns:
        Dictionary with basic stock features or None if error
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            logger.warning(f"No historical data found for {ticker}")
            return None
        
        latest_data = hist.iloc[-1]
        
        # Basic OHLCV features
        features = {
            'open': float(latest_data['Open']),
            'high': float(latest_data['High']),
            'low': float(latest_data['Low']),
            'close': float(latest_data['Close']),
            'volume': float(latest_data['Volume'])
        }
        
        # Moving averages
        if len(hist) >= 10:
            features['ma10'] = float(hist['Close'].rolling(window=10).mean().iloc[-1])
        else:
            features['ma10'] = features['close']
            
        if len(hist) >= 50:
            features['ma50'] = float(hist['Close'].rolling(window=50).mean().iloc[-1])
        else:
            features['ma50'] = features['ma10']
        
        # Returns calculation
        if len(hist) > 1:
            prev_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            features['returns'] = float((current_close - prev_close) / prev_close)
        else:
            features['returns'] = 0.0
        
        # Volatility calculation
        daily_returns = hist['Close'].pct_change().dropna()
        if len(daily_returns) >= 20:
            features['volatility'] = float(daily_returns.rolling(window=20).std().iloc[-1])
        else:
            features['volatility'] = float(daily_returns.std()) if len(daily_returns) > 0 else 0.02
        
        # Handle NaN values
        for key, value in features.items():
            if pd.isna(value):
                if key == 'volatility':
                    features[key] = 0.02
                elif key in ['ma10', 'ma50']:
                    features[key] = features['close']
                else:
                    features[key] = 0.0
        
        logger.info(f"Successfully extracted features for {ticker}")
        return features
        
    except Exception as e:
        logger.error(f"Error extracting features for {ticker}: {str(e)}")
        return None

def calculate_technical_indicators(hist_data: pd.DataFrame) -> Dict:
    """
    Calculate various technical indicators from historical data
    
    Args:
        hist_data: Historical stock data DataFrame
        
    Returns:
        Dictionary with technical indicators
    """
    try:
        indicators = {}
        
        # RSI calculation
        def calculate_rsi(prices: pd.Series, window: int = 14) -> float:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        
        # MACD calculation
        def calculate_macd(prices: pd.Series) -> Tuple[float, float, float]:
            exp1 = prices.ewm(span=12).mean()
            exp2 = prices.ewm(span=26).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            return (
                float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0.0,
                float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0,
                float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else 0.0
            )
        
        # Bollinger Bands
        def calculate_bollinger_bands(prices: pd.Series, window: int = 20) -> Tuple[float, float, float]:
            rolling_mean = prices.rolling(window=window).mean()
            rolling_std = prices.rolling(window=window).std()
            upper_band = rolling_mean + (rolling_std * 2)
            lower_band = rolling_mean - (rolling_std * 2)
            
            return (
                float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else 0.0,
                float(rolling_mean.iloc[-1]) if not pd.isna(rolling_mean.iloc[-1]) else 0.0,
                float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else 0.0
            )
        
        # Calculate indicators
        if len(hist_data) >= 14:
            indicators['rsi'] = calculate_rsi(hist_data['Close'])
        else:
            indicators['rsi'] = 50.0
        
        if len(hist_data) >= 26:
            macd, signal, histogram = calculate_macd(hist_data['Close'])
            indicators['macd'] = macd
            indicators['macd_signal'] = signal
            indicators['macd_histogram'] = histogram
        else:
            indicators['macd'] = 0.0
            indicators['macd_signal'] = 0.0
            indicators['macd_histogram'] = 0.0
        
        if len(hist_data) >= 20:
            bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(hist_data['Close'])
            indicators['bb_upper'] = bb_upper
            indicators['bb_middle'] = bb_middle
            indicators['bb_lower'] = bb_lower
            
            # Bollinger Band position
            current_price = hist_data['Close'].iloc[-1]
            if bb_upper != bb_lower:
                indicators['bb_position'] = (current_price - bb_lower) / (bb_upper - bb_lower)
            else:
                indicators['bb_position'] = 0.5
        else:
            current_price = hist_data['Close'].iloc[-1]
            indicators['bb_upper'] = current_price * 1.05
            indicators['bb_middle'] = current_price
            indicators['bb_lower'] = current_price * 0.95
            indicators['bb_position'] = 0.5
        
        logger.info("Successfully calculated technical indicators")
        return indicators
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        return {}

def get_comprehensive_features(ticker: str, period: str = "60d") -> Optional[Dict]:
    """
    Get comprehensive features including basic features and technical indicators
    
    Args:
        ticker: Stock ticker symbol
        period: Period for historical data
        
    Returns:
        Dictionary with comprehensive features or None if error
    """
    try:
        # Get historical data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            logger.warning(f"No historical data found for {ticker}")
            return None
        
        # Get basic features
        basic_features = get_stock_basic_features(ticker, period)
        if not basic_features:
            return None
        
        # Get technical indicators
        technical_indicators = calculate_technical_indicators(hist)
        
        # Combine all features
        comprehensive_features = {
            **basic_features,
            **technical_indicators
        }
        
        # Add metadata
        comprehensive_features['data_points'] = len(hist)
        comprehensive_features['period'] = period
        comprehensive_features['last_updated'] = datetime.now().isoformat()
        
        logger.info(f"Successfully compiled comprehensive features for {ticker}")
        return comprehensive_features
        
    except Exception as e:
        logger.error(f"Error getting comprehensive features for {ticker}: {str(e)}")
        return None

def validate_features(features: Dict, required_features: List[str]) -> bool:
    """
    Validate that all required features are present and not NaN
    
    Args:
        features: Dictionary of features
        required_features: List of required feature names
        
    Returns:
        True if all required features are valid, False otherwise
    """
    try:
        for feature in required_features:
            if feature not in features:
                logger.warning(f"Missing required feature: {feature}")
                return False
            
            value = features[feature]
            if pd.isna(value) or (isinstance(value, (int, float)) and np.isinf(value)):
                logger.warning(f"Invalid value for feature {feature}: {value}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating features: {str(e)}")
        return False

def get_feature_importance_info() -> Dict:
    """
    Get information about feature importance for stock prediction
    
    Returns:
        Dictionary with feature importance information
    """
    return {
        "primary_features": [
            "open", "high", "low", "volume", "ma10", "ma50", "returns", "volatility"
        ],
        "technical_indicators": [
            "rsi", "macd", "macd_signal", "macd_histogram", 
            "bb_upper", "bb_middle", "bb_lower", "bb_position"
        ],
        "feature_descriptions": {
            "open": "Opening price of the stock",
            "high": "Highest price during the period",
            "low": "Lowest price during the period",
            "volume": "Trading volume",
            "ma10": "10-day moving average",
            "ma50": "50-day moving average",
            "returns": "Daily returns (price change percentage)",
            "volatility": "Price volatility (20-day rolling standard deviation)",
            "rsi": "Relative Strength Index (14-day)",
            "macd": "MACD line",
            "macd_signal": "MACD signal line",
            "macd_histogram": "MACD histogram",
            "bb_upper": "Bollinger Band upper line",
            "bb_middle": "Bollinger Band middle line (20-day MA)",
            "bb_lower": "Bollinger Band lower line",
            "bb_position": "Position within Bollinger Bands (0-1)"
        }
    }