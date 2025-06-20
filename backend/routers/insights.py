from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, List, Any
from utils.constants import TICKER_LIST
from utils.sentiment import get_sentiment_for_ticker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

insights_router = APIRouter()

def get_stock_prediction_data(ticker: str) -> Dict[str, Any]:
    """Get prediction data for a single ticker"""
    try:
        from routers.predict import predict_stock_price
        return predict_stock_price(ticker)
    except ImportError as e:
        logger.error(f"Failed to import predict_stock_price: {e}")
        return {}
    except Exception as e:
        logger.warning(f"Failed to get prediction for {ticker}: {e}")
        return {}

def parse_confidence(confidence_str: str) -> int:
    """Parse confidence string to integer"""
    try:
        # Remove % sign and convert to int
        return int(confidence_str.replace('%', '').strip())
    except (ValueError, AttributeError):
        return 0

def categorize_stock(ticker: str, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Categorize a stock based on prediction data"""
    trend = prediction_data.get("trend", "").strip()
    confidence_str = prediction_data.get("confidence", "0%")
    confidence = parse_confidence(confidence_str)
    
    return {
        "ticker": ticker,
        "trend": trend,
        "confidence": confidence,
        "current_price": prediction_data.get("current_price"),
        "predicted_price": prediction_data.get("predicted_price"),
        "prediction_data": prediction_data
    }

@insights_router.get("/insights")
def get_insights():
    """Get market insights including bullish, potential buys, and underperforming stocks"""
    try:
        bullish = []
        potential_buys = []
        underperforming = []
        processing_errors = []
        
        logger.info(f"Processing insights for {len(TICKER_LIST)} tickers")
        
        for ticker in TICKER_LIST:
            try:
                # Get prediction data
                prediction_data = get_stock_prediction_data(ticker)
                
                if not prediction_data:
                    processing_errors.append(f"No prediction data for {ticker}")
                    continue
                
                # Categorize the stock
                stock_info = categorize_stock(ticker, prediction_data)
                
                trend = stock_info["trend"]
                confidence = stock_info["confidence"]
                
                if trend.lower() == "bullish":
                    bullish.append(stock_info)
                    # High confidence bullish stocks are potential buys
                    if confidence >= 75:  # Lowered threshold slightly
                        potential_buys.append(stock_info)
                elif trend.lower() == "bearish":
                    underperforming.append(stock_info)
                
                logger.debug(f"Processed {ticker}: {trend} ({confidence}%)")
                
            except Exception as e:
                error_msg = f"Error processing {ticker}: {str(e)}"
                logger.warning(error_msg)
                processing_errors.append(error_msg)
        
        # Sort by confidence (highest first)
        bullish.sort(key=lambda x: x["confidence"], reverse=True)
        potential_buys.sort(key=lambda x: x["confidence"], reverse=True)
        underperforming.sort(key=lambda x: x["confidence"], reverse=True)
        
        result = {
            "summary": {
                "total_analyzed": len(TICKER_LIST),
                "bullish_count": len(bullish),
                "potential_buys_count": len(potential_buys),
                "underperforming_count": len(underperforming),
                "errors_count": len(processing_errors)
            },
            "top_bullish": bullish[:10],  # Top 10 bullish stocks
            "potential_buys": potential_buys[:5],  # Top 5 potential buys
            "underperforming": underperforming[:10],  # Top 10 underperforming
            "processing_errors": processing_errors if processing_errors else None
        }
        
        logger.info(f"Insights generated: {result['summary']}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@insights_router.get("/insights/detailed/{ticker}")
def get_detailed_insights(ticker: str):
    """Get detailed insights for a specific ticker including sentiment analysis"""
    try:
        ticker = ticker.upper()
        logger.info(f"Getting detailed insights for {ticker}")
        
        # Get prediction data
        prediction_data = get_stock_prediction_data(ticker)
        
        if not prediction_data:
            raise HTTPException(status_code=404, detail=f"No prediction data found for {ticker}")
        
        # Get sentiment data
        try:
            sentiment_data = get_sentiment_for_ticker(ticker)
        except Exception as e:
            logger.warning(f"Failed to get sentiment for {ticker}: {e}")
            sentiment_data = {
                "ticker": ticker,
                "summary": {"positive": 0, "neutral": 0, "negative": 0},
                "articles": [],
                "message": f"Sentiment analysis failed: {str(e)}"
            }
        
        # Categorize the stock
        stock_info = categorize_stock(ticker, prediction_data)
        
        # Calculate overall sentiment score
        sentiment_summary = sentiment_data.get("summary", {})
        total_articles = sum(sentiment_summary.values())
        
        if total_articles > 0:
            sentiment_score = (
                sentiment_summary.get("positive", 0) * 1 + 
                sentiment_summary.get("neutral", 0) * 0 + 
                sentiment_summary.get("negative", 0) * -1
            ) / total_articles
        else:
            sentiment_score = 0
        
        # Generate recommendation
        trend = stock_info["trend"].lower()
        confidence = stock_info["confidence"]
        
        if trend == "bullish" and confidence >= 75 and sentiment_score >= 0.2:
            recommendation = "Strong Buy"
        elif trend == "bullish" and confidence >= 60:
            recommendation = "Buy"
        elif trend == "bearish" and confidence >= 75 and sentiment_score <= -0.2:
            recommendation = "Strong Sell"
        elif trend == "bearish" and confidence >= 60:
            recommendation = "Sell"
        else:
            recommendation = "Hold"
        
        return {
            "ticker": ticker,
            "recommendation": recommendation,
            "prediction": stock_info,
            "sentiment": sentiment_data,
            "sentiment_score": round(sentiment_score, 2),
            "analysis": {
                "technical_signal": f"{trend.title()} ({confidence}%)",
                "news_sentiment": f"{sentiment_score:.2f} ({total_articles} articles)",
                "recommendation_reason": f"Based on {trend} trend with {confidence}% confidence and sentiment score of {sentiment_score:.2f}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting detailed insights for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get detailed insights: {str(e)}")

@insights_router.get("/insights/summary")
def get_market_summary():
    """Get a quick market summary"""
    try:
        insights_data = get_insights()
        
        summary = insights_data["summary"]
        top_bullish = insights_data["top_bullish"][:3]  # Top 3
        top_underperforming = insights_data["underperforming"][:3]  # Top 3
        
        return {
            "market_overview": {
                "total_stocks_analyzed": summary["total_analyzed"],
                "bullish_percentage": round((summary["bullish_count"] / summary["total_analyzed"]) * 100, 1),
                "bearish_percentage": round((summary["underperforming_count"] / summary["total_analyzed"]) * 100, 1)
            },
            "top_performers": [
                {
                    "ticker": stock["ticker"],
                    "trend": stock["trend"],
                    "confidence": stock["confidence"]
                } for stock in top_bullish
            ],
            "worst_performers": [
                {
                    "ticker": stock["ticker"], 
                    "trend": stock["trend"],
                    "confidence": stock["confidence"]
                } for stock in top_underperforming
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting market summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market summary: {str(e)}")