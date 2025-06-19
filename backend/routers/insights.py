from fastapi import APIRouter
import logging
from utils.constants import TICKER_LIST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

insights_router = APIRouter()

@insights_router.get("/insights")
def get_insights():
    bullish = []
    potential_buys = []
    underperforming = []

    for ticker in TICKER_LIST:
        try:
            from routers.predict import predict_stock_price
            data = predict_stock_price(ticker)

            trend = data.get("trend", "")
            confidence_str = data.get("confidence", "0%").replace('%', '')
            confidence = int(confidence_str)

            if trend == "Bullish":
                bullish.append(ticker)
                if confidence >= 80:
                    potential_buys.append(ticker)
            elif trend == "Bearish":
                underperforming.append(ticker)
        except Exception as e:
            logger.warning(f"Skipping {ticker}: {e}")

    return {
        "top_bullish": bullish,
        "potential_buys": potential_buys,
        "underperforming": underperforming
    }
