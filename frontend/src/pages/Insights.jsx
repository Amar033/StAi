import axios from 'axios';
import { Activity, AlertTriangle, BarChart3, Target, TrendingUp, Zap } from 'lucide-react';
import React, { useEffect, useState } from 'react';

const baseURL = import.meta.env.VITE_API_BASE_URL;

const StockCard = ({ stock, type }) => {
  const getTypeConfig = (type) => {
    switch(type) {
      case 'bullish':
        return {
          gradient: 'from-green-500/20 to-emerald-600/20',
          borderColor: 'border-green-500/30',
          textColor: 'text-green-400',
          icon: TrendingUp,
          iconBg: 'bg-green-500/20',
          title: 'BULLISH'
        };
      case 'buy':
        return {
          gradient: 'from-primary-500/20 to-secondary-500/20',
          borderColor: 'border-primary-500/30',
          textColor: 'text-primary-400',
          icon: Target,
          iconBg: 'bg-primary-500/20',
          title: 'BUY'
        };
      case 'underperforming':
        return {
          gradient: 'from-red-500/20 to-rose-600/20',
          borderColor: 'border-red-500/30',
          textColor: 'text-red-400',
          icon: AlertTriangle,
          iconBg: 'bg-red-500/20',
          title: 'WATCH'
        };
      default:
        return {
          gradient: 'from-background-700/20 to-background-600/20',
          borderColor: 'border-background-600/30',
          textColor: 'text-text-400',
          icon: BarChart3,
          iconBg: 'bg-background-600/20',
          title: 'NEUTRAL'
        };
    }
  };

  const config = getTypeConfig(type);
  const IconComponent = config.icon;
  
  const priceChange = stock.predicted_price && stock.current_price 
    ? ((stock.predicted_price - stock.current_price) / stock.current_price * 100).toFixed(2)
    : null;

  // Handle confidence display
  let displayConfidence = stock.confidence || 0;
  if (typeof displayConfidence === 'string') {
    displayConfidence = parseFloat(displayConfidence.replace('%', ''));
  }
  if (displayConfidence <= 1) {
    displayConfidence = displayConfidence * 100;
  }

  return (
    <div className="group relative">
      <div className={`absolute inset-0 bg-gradient-to-br ${config.gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
      <div className={`relative p-6 bg-background-800/60 backdrop-blur-sm rounded-2xl border ${config.borderColor} hover:border-opacity-50 transition-all duration-300`}>
        
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 ${config.iconBg} rounded-lg`}>
              <IconComponent className={`w-5 h-5 ${config.textColor}`} />
            </div>
            <div>
              <h3 className="text-lg font-bold text-text-100">{stock.ticker || 'Unknown'}</h3>
              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${config.iconBg} ${config.textColor}`}>
                {config.title}
              </span>
            </div>
          </div>
          
          {displayConfidence > 0 && (
            <div className="text-right">
              <div className="text-xs text-text-400 mb-1">Confidence</div>
              <div className={`text-lg font-bold ${config.textColor}`}>
                {Math.round(displayConfidence)}%
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          {stock.current_price && (
            <div className="p-3 bg-background-700/50 rounded-xl">
              <div className="text-xs text-text-400 mb-1">Current</div>
              <div className="text-text-100 font-semibold">${stock.current_price}</div>
            </div>
          )}
          {stock.predicted_price && (
            <div className="p-3 bg-background-700/50 rounded-xl">
              <div className="text-xs text-text-400 mb-1">Target</div>
              <div className={`font-semibold ${config.textColor}`}>${stock.predicted_price}</div>
            </div>
          )}
        </div>

        {priceChange && (
          <div className="flex items-center justify-between p-3 bg-background-700/30 rounded-xl">
            <span className="text-text-400 text-sm">Potential Return</span>
            <span className={`text-sm font-bold ${priceChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {priceChange >= 0 ? '+' : ''}{priceChange}%
            </span>
          </div>
        )}

        {stock.trend && (
          <div className="mt-3 flex items-center justify-center">
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${config.iconBg} ${config.textColor}`}>
              {stock.trend.toUpperCase()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, subtitle, icon: Icon, color }) => (
  <div className="group relative">
    <div className={`absolute inset-0 bg-gradient-to-br ${color}/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
    <div className="relative p-6 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30 hover:border-opacity-50 transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-text-400 text-sm mb-1">{title}</div>
          <div className={`text-3xl font-bold ${color} mb-1`}>{value}</div>
          {subtitle && <div className="text-text-400 text-xs">{subtitle}</div>}
        </div>
        <div className={`p-3 bg-${color.split('-')[1]}-500/20 rounded-xl`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  </div>
);

const InsightSection = ({ title, stocks, type, description, icon: Icon, color }) => (
  <div className="mb-12">
    <div className="group relative mb-6">
      <div className={`absolute inset-0 bg-gradient-to-r ${color}/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
      <div className="relative p-6 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30">
        <div className="flex items-center gap-3 mb-2">
          <div className={`p-2 bg-${color.split('-')[1]}-500/20 rounded-lg`}>
            <Icon className={`w-6 h-6 ${color}`} />
          </div>
          <h2 className="text-2xl font-semibold text-text-100">{title}</h2>
          <div className={`ml-auto px-3 py-1 bg-${color.split('-')[1]}-500/20 ${color} rounded-full text-sm font-medium`}>
            {stocks.length} stocks
          </div>
        </div>
        <p className="text-text-400">{description}</p>
      </div>
    </div>

    {stocks.length === 0 ? (
      <div className="group relative">
        <div className="absolute inset-0 bg-gradient-to-br from-background-700/20 to-background-600/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="relative p-12 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30 text-center">
          <div className="p-4 bg-background-700/50 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <BarChart3 className="w-8 h-8 text-text-400" />
          </div>
          <p className="text-text-400">No data available for this category</p>
        </div>
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
      <div className="min-h-screen bg-background-950 text-text-50 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-background-900/50 to-background-950 pointer-events-none"></div>
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="p-4 bg-primary-500/20 rounded-full w-16 h-16 mx-auto mb-6 flex items-center justify-center">
              <Activity className="w-8 h-8 text-primary-400 animate-pulse" />
            </div>
            <h2 className="text-xl font-semibold text-text-100 mb-2">Analyzing Market Data</h2>
            <p className="text-text-400">Gathering insights from multiple sources...</p>
          </div>
        </div>
      </div>
    );
  }

  const totalStocks = (insights?.top_bullish?.length || 0) + 
                    (insights?.potential_buys?.length || 0) + 
                    (insights?.underperforming?.length || 0);

  return (
    <div className="min-h-screen bg-background-950 text-text-50 relative overflow-hidden">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-background-900/50 to-background-950 pointer-events-none"></div>
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-accent-500/20 rounded-full border border-accent-500/30">
              <Zap className="w-8 h-8 text-accent-400" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-400 via-secondary-400 to-accent-400 bg-clip-text text-transparent">
              AI Insights
            </h1>
          </div>
          <p className="text-xl text-text-300 font-medium">Market Intelligence Dashboard</p>
          <p className="text-text-400 mt-2">Real-time analysis powered by machine learning</p>
        </header>

        {!insights ? (
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-rose-600/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="relative text-center py-16 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30">
              <div className="p-4 bg-red-500/20 rounded-full w-16 h-16 mx-auto mb-6 flex items-center justify-center">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <h2 className="text-xl font-semibold text-text-100 mb-2">Unable to Load Market Data</h2>
              <p className="text-text-400">Please check your connection and try again</p>
            </div>
          </div>
        ) : (
          <>
            {/* Market Summary */}
            <section className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
              <MetricCard 
                title="Bullish Signals" 
                value={insights.top_bullish?.length || 0}
                subtitle="Strong momentum"
                icon={TrendingUp}
                color="text-green-400"
              />
              <MetricCard 
                title="Buy Opportunities" 
                value={insights.potential_buys?.length || 0}
                subtitle="Undervalued picks"
                icon={Target}
                color="text-primary-400"
              />
              <MetricCard 
                title="Watch List" 
                value={insights.underperforming?.length || 0}
                subtitle="Need attention"
                icon={AlertTriangle}
                color="text-red-400"
              />
              <MetricCard 
                title="Total Analyzed" 
                value={totalStocks}
                subtitle="Live tracking"
                icon={BarChart3}
                color="text-accent-400"
              />
            </section>

            {/* Insights Sections */}
            <InsightSection 
              title="🔥 Top Bullish Stocks"
              description="Stocks showing strong upward momentum with positive technical indicators and market sentiment"
              stocks={insights.top_bullish || []}
              type="bullish"
              icon={TrendingUp}
              color="text-green-400"
            />

            <InsightSection 
              title="💎 Premium Buy Opportunities"
              description="Carefully selected undervalued stocks with strong fundamentals and growth potential"
              stocks={insights.potential_buys || []}
              type="buy"
              icon={Target}
              color="text-primary-400"
            />

            <InsightSection 
              title="⚠️ Stocks to Watch"
              description="Stocks experiencing volatility or showing bearish patterns that require attention"
              stocks={insights.underperforming || []}
              type="underperforming"
              icon={AlertTriangle}
              color="text-red-400"
            />
          </>
        )}

        {/* Footer */}
        <footer className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-background-800/40 backdrop-blur-sm rounded-full border border-background-600/30">
            <span className="text-text-400">⚠️ AI-generated insights for research purposes only</span>
            <span className="text-primary-400">•</span>
            <span className="text-text-400">Not financial advice</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Insights;