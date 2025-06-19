import { MinusCircle, TrendingDown, TrendingUp } from "lucide-react";
import React from "react";
import MiniChart from "./MiniChart";

const StockComparisonCard = ({ symbol, stockData }) => {
  if (!stockData || stockData.error) {
    return (
      <div className="p-6 bg-background-800/40 rounded-xl border border-background-700 text-red-400">
        <h2 className="text-xl font-semibold">{symbol}</h2>
        <p className="mt-2 text-sm">⚠️ Could not fetch data.</p>
      </div>
    );
  }

  const trendColor =
    stockData.trend === "Bullish"
      ? "border-green-500 shadow-green-500/30"
      : stockData.trend === "Bearish"
      ? "border-red-500 shadow-red-500/30"
      : "border-yellow-400 shadow-yellow-400/30";

  const TrendIcon =
    stockData.trend === "Bullish"
      ? TrendingUp
      : stockData.trend === "Bearish"
      ? TrendingDown
      : MinusCircle;

  return (
    <div
      className={`p-5 rounded-2xl bg-background-800 border-2 shadow-md ${trendColor} transition-all duration-300`}
    >
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-2xl font-bold text-primary-400">{stockData.symbol}</h2>
        <TrendIcon className="w-6 h-6 text-text-400" />
      </div>
      <p className="text-text-300 text-sm mb-3">{stockData.name}</p>

      <div className="text-sm space-y-1 mb-4">
        <p><span className="text-text-400">Current:</span> ${stockData.price}</p>
        <p><span className="text-text-400">Prediction:</span> <span className="text-accent-400">${stockData.prediction}</span></p>
        <p><span className="text-text-400">Trend:</span> {stockData.trend}</p>
        <p><span className="text-text-400">Confidence:</span> {stockData.confidence}</p>
        <p><span className="text-text-400">Sentiment:</span> {stockData.sentimentScore}</p>
      </div>

      <MiniChart symbol={symbol} />
    </div>
  );
};

export default StockComparisonCard;
