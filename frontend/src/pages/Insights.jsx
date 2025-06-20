import axios from 'axios';
import React, { useEffect, useState } from 'react';

const baseURL = import.meta.env.VITE_API_BASE_URL;

const StockCard = ({ stock, type }) => {
  const getTypeConfig = (type) => {
    switch(type) {
      case 'bullish':
        return {
          bgGradient: 'from-green-500/20 to-emerald-600/20',
          borderColor: 'border-green-400',
          textColor: 'text-green-400',
          icon: '📈',
          badgeColor: 'bg-green-500/20 text-green-300'
        };
      case 'buy':
        return {
          bgGradient: 'from-blue-500/20 to-cyan-600/20',
          borderColor: 'border-blue-400',
          textColor: 'text-blue-400',
          icon: '💎',
          badgeColor: 'bg-blue-500/20 text-blue-300'
        };
      case 'underperforming':
        return {
          bgGradient: 'from-red-500/20 to-rose-600/20',
          borderColor: 'border-red-400',
          textColor: 'text-red-400',
          icon: '📉',
          badgeColor: 'bg-red-500/20 text-red-300'
        };
      default:
        return {
          bgGradient: 'from-gray-500/20 to-slate-600/20',
          borderColor: 'border-gray-400',
          textColor: 'text-gray-400',
          icon: '📊',
          badgeColor: 'bg-gray-500/20 text-gray-300'
        };
    }
  };

  const config = getTypeConfig(type);
  const priceChange = stock.predicted_price && stock.current_price 
    ? ((stock.predicted_price - stock.current_price) / stock.current_price * 100).toFixed(2)
    : null;

  return (
    <div className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${config.bgGradient} backdrop-blur-sm border ${config.borderColor} p-4 transition-all duration-300 hover:scale-105 hover:shadow-xl`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <h3 className="text-lg font-bold text-white">{stock.ticker || 'Unknown'}</h3>
            {stock.trend && (
              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${config.badgeColor}`}>
                {stock.trend}
              </span>
            )}
          </div>
        </div>
        {stock.confidence && (
          <div className="text-right">
            <div className="text-xs text-gray-400">Confidence</div>
            <div className={`text-sm font-semibold ${config.textColor}`}>
              {(stock.confidence * 100).toFixed(0)}%
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        {stock.current_price && (
          <div>
            <div className="text-gray-400">Current Price</div>
            <div className="text-white font-semibold">${stock.current_price}</div>
          </div>
        )}
        {stock.predicted_price && (
          <div>
            <div className="text-gray-400">Target Price</div>
            <div className={`font-semibold ${config.textColor}`}>${stock.predicted_price}</div>
          </div>
        )}
      </div>

      {priceChange && (
        <div className="mt-3 pt-3 border-t border-gray-600/30">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs">Potential Return</span>
            <span className={`text-sm font-bold ${priceChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {priceChange >= 0 ? '+' : ''}{priceChange}%
            </span>
          </div>
        </div>
      )}

      {/* Decorative element */}
      <div className={`absolute top-0 right-0 w-20 h-20 ${config.bgGradient} opacity-10 rounded-full -translate-y-10 translate-x-10`}></div>
    </div>
  );
};

const MarketSummaryCard = ({ title, value, change, icon, color }) => (
  <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700">
    <div className="flex items-center justify-between">
      <div>
        <div className="text-gray-400 text-sm">{title}</div>
        <div className="text-white text-xl font-bold">{value}</div>
        {change && (
          <div className={`text-sm font-medium ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {change >= 0 ? '+' : ''}{change}%
          </div>
        )}
      </div>
      <div className={`text-3xl ${color}`}>{icon}</div>
    </div>
  </div>
);

const InsightSection = ({ title, stocks, type, description }) => (
  <div className="mb-8">
    <div className="mb-4">
      <h2 className="text-2xl font-bold text-white mb-2">{title}</h2>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
    {stocks.length === 0 ? (
      <div className="bg-gray-800/30 rounded-xl p-8 text-center border border-gray-700">
        <div className="text-4xl mb-2">📊</div>
        <p className="text-gray-400">No data available at this time</p>
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stocks.map((stock, index) => (
          <StockCard key={stock.ticker || index} stock={stock} type={type} />
        ))}
      </div>
    )}
  </div>
);

const Insights = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${baseURL}/insights`)
      .then(res => {
        setInsights(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <p className="text-gray-400">Analyzing market data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-900/80 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                AI Stock Analysis
              </h1>
              <p className="text-gray-400 mt-1">Real-time insights powered by machine learning</p>
            </div>
            <div className="text-right">
              <div className="text-gray-400 text-sm">Last Updated</div>
              <div className="text-white font-medium">{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {!insights ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-xl font-semibold text-white mb-2">Unable to Load Market Data</h2>
            <p className="text-gray-400">Please check your connection and try again</p>
          </div>
        ) : (
          <>
            {/* Market Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <MarketSummaryCard 
                title="Bullish Signals" 
                value={insights.top_bullish?.length || 0}
                icon="🔥" 
                color="text-green-400"
              />
              <MarketSummaryCard 
                title="Buy Opportunities" 
                value={insights.potential_buys?.length || 0}
                icon="💎" 
                color="text-blue-400"
              />
              <MarketSummaryCard 
                title="Underperforming" 
                value={insights.underperforming?.length || 0}
                icon="⚠️" 
                color="text-red-400"
              />
              <MarketSummaryCard 
                title="Total Analyzed" 
                value={(insights.top_bullish?.length || 0) + (insights.potential_buys?.length || 0) + (insights.underperforming?.length || 0)}
                icon="📈" 
                color="text-purple-400"
              />
            </div>

            {/* Insights Sections */}
            <InsightSection 
              title="🔥 Top Bullish Stocks"
              description="Stocks showing strong upward momentum and positive market sentiment"
              stocks={insights.top_bullish || []}
              type="bullish"
            />

            <InsightSection 
              title="💎 Potential Buy Opportunities"
              description="Undervalued stocks with strong fundamentals and growth potential"
              stocks={insights.potential_buys || []}
              type="buy"
            />

            <InsightSection 
              title="⚠️ Underperforming Stocks"
              description="Stocks experiencing challenges or showing bearish patterns"
              stocks={insights.underperforming || []}
              type="underperforming"
            />
          </>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-900/80 backdrop-blur-sm border-t border-gray-700 mt-12">
        <div className="container mx-auto px-6 py-4">
          <div className="text-center text-gray-400 text-sm">
            <p>⚠️ This analysis is for informational purposes only and should not be considered as financial advice.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Insights;