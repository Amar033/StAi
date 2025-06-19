import axios from 'axios';
import { Activity, BarChart3, DollarSign, Search, TrendingUp } from 'lucide-react';
import { default as React, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MiniChart from '../components/MiniChart';
const baseURL = import.meta.env.VITE_API_BASE_URL;

const Home = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const [trendingData, setTrendingData] = useState({});
  const [predictionsData, setPredictionsData] = useState({});
  const [sentimentData, setSentimentData] = useState({});
  const [loading, setLoading] = useState(true);

  const tickers = ["AAPL", "GOOGL", "TSLA"];

  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        // Fetch trending data
        const trendingRes = {};
        const predictionsRes = {};
        const sentimentRes = {};

        for (let ticker of tickers) {
          try {
            // Fetch price history
            const { data: priceData } = await axios.get(`${baseURL}/price-history/${ticker}`);
            trendingRes[ticker] = priceData;

            // Fetch predictions
            const { data: predictionData } = await axios.get(`${baseURL}/predict/${ticker}`);
            predictionsRes[ticker] = predictionData;

            // Fetch sentiment
            const { data: sentimentInfo } = await axios.get(`${baseURL}/sentiment/${ticker}`);
            sentimentRes[ticker] = sentimentInfo;
          } catch (error) {
            console.error(`Error fetching data for ${ticker}:`, error);
            // Set default values if API fails
            predictionsRes[ticker] = { prediction: 0, confidence: 0, trend: 'neutral' };
            sentimentRes[ticker] = { sentiment_score: 0, articles: [] };
          }
        }

        setTrendingData(trendingRes);
        setPredictionsData(predictionsRes);
        setSentimentData(sentimentRes);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  const handleAnalyze = () => {
    if (searchQuery.trim()) {
      navigate(`/search/${searchQuery.trim().toUpperCase()}`);
    }
  };

  // Fixed calculateAggregateMetrics function for Home.jsx

const calculateAggregateMetrics = () => {
  const predictions = Object.values(predictionsData);
  const sentiments = Object.values(sentimentData);

  if (predictions.length === 0 || sentiments.length === 0) {
    return {
      avgConfidence: 0,
      bullishCount: 0,
      avgSentiment: 0,
      newsCount: 0
    };
  }

  // Extract and normalize confidence values
  const validConfidences = predictions
    .map((p) => {
      let confidence = p.confidence;
      // Handle confidence as string (e.g., "85%")
      if (typeof confidence === 'string') {
        confidence = parseFloat(confidence.replace('%', ''));
      }
      // Handle confidence as number
      if (typeof confidence === 'number' && !isNaN(confidence)) {
        // If confidence is between 0-1, convert to percentage
        if (confidence <= 1) {
          confidence = confidence * 100;
        }
        return confidence;
      }
      return null;
    })
    .filter((c) => c !== null && c >= 0 && c <= 100);

  const avgConfidence = validConfidences.length > 0 
    ? Math.round(validConfidences.reduce((sum, c) => sum + c, 0) / validConfidences.length)
    : 0;

  const bullishCount = predictions.filter(p => 
    p.trend === 'bullish' || p.trend === 'up' || p.trend === 'Bullish'
  ).length;

  const avgSentiment = sentiments.reduce((sum, s) => sum + (s.sentiment_score || 0), 0) / sentiments.length;
  const newsCount = sentiments.reduce((sum, s) => sum + (s.articles?.length || 0), 0);

  return {
    avgConfidence,
    bullishCount,
    avgSentiment: Math.round(avgSentiment * 100) / 100,
    newsCount
  };
};

// Also fix the getBestPrediction function
const getBestPrediction = () => {
  const predictions = Object.entries(predictionsData);
  if (predictions.length === 0) return { ticker: '--', prediction: '--', confidence: 0, trend: '--' };

  const bestPrediction = predictions.reduce((best, [ticker, data]) => {
    let confidence = data.confidence;
    
    // Handle confidence as string (e.g., "85%")
    if (typeof confidence === 'string') {
      confidence = parseFloat(confidence.replace('%', ''));
    }
    
    // Handle confidence as number
    if (typeof confidence === 'number' && !isNaN(confidence)) {
      // If confidence is between 0-1, convert to percentage
      if (confidence <= 1) {
        confidence = confidence * 100;
      }
      
      let bestConfidence = best.confidence;
      if (typeof bestConfidence === 'string') {
        bestConfidence = parseFloat(bestConfidence.replace('%', ''));
      }
      if (bestConfidence <= 1) {
        bestConfidence = bestConfidence * 100;
      }
      
      if (confidence > (bestConfidence || 0)) {
        return { ticker, ...data, confidence };
      }
    }
    return best;
  }, { ticker: '--', prediction: '--', confidence: 0, trend: '--' });

  return bestPrediction;
};
const metrics = calculateAggregateMetrics();
  const bestPrediction = getBestPrediction();

  return (
    <div className="min-h-screen bg-background-950 text-text-50 relative overflow-hidden">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-background-900/50 to-background-950 pointer-events-none"></div>
      
      <div className="relative z-10 p-6 max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-primary-500/10 rounded-full border border-primary-500/20">
              <Activity className="w-8 h-8 text-primary-400" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-400 via-secondary-400 to-accent-400 bg-clip-text text-transparent">
              StAI
            </h1>
          </div>
          <p className="text-xl text-text-300 font-medium">Stock Intelligence Platform</p>
          <p className="text-text-400 mt-2">Live market insights & AI-powered predictions</p>
        </header>

        {/* Search Section */}
        <section className="mb-12">
          <div className="max-w-2xl mx-auto">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-secondary-500/20 rounded-xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative flex items-center">
                <Search className="absolute left-4 w-5 h-5 text-text-400 z-10" />
                <input
                  type="text"
                  placeholder="Search stocks (e.g., AAPL, TSLA, NVDA)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-6 py-4 bg-background-800/80 backdrop-blur-sm text-text-100 placeholder-text-400 border border-background-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all duration-300"
                />
                <button onClick={handleAnalyze} className="absolute right-2 px-6 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-text-50 rounded-lg hover:from-primary-400 hover:to-secondary-400 transition-all duration-300 font-medium">
                  Analyze
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Main Content Grid */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Price Chart - Large Card */}
          <div className="lg:col-span-2 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 to-secondary-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative p-6 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30 hover:border-primary-500/30 transition-all duration-300">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary-500/20 rounded-lg">
                      <BarChart3 className="w-6 h-6 text-primary-400" />
                    </div>
                    <h2 className="text-2xl font-semibold text-text-100">Price Charts</h2>
                  </div>
                  <div className="flex items-center gap-2 text-accent-400">
                    <TrendingUp className="w-5 h-5" />
                    <span className="text-sm font-medium">Real-time</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <MiniChart symbol="AAPL" />
                  <MiniChart symbol="GOOGL" />
                  <MiniChart symbol="TSLA" />
                </div>
              </div>
            </div>
          </div>

          {/* AI Prediction Card */}
          <div className="group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-accent-500/10 to-secondary-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative p-6 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30 hover:border-accent-500/30 transition-all duration-300 h-full">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-accent-500/20 rounded-lg">
                    <DollarSign className="w-6 h-6 text-accent-400" />
                  </div>
                  <h2 className="text-xl font-semibold text-text-100">Top AI Prediction</h2>
                </div>
                
                <div className="text-center">
                  {loading ? (
                    <div className="text-2xl font-bold text-text-400 mb-2">Loading...</div>
                  ) : (
                    <>
                      <div className="text-sm text-text-400 mb-2">{bestPrediction.ticker}</div>
                      <div className="text-4xl font-bold bg-gradient-to-r from-accent-400 to-secondary-400 bg-clip-text text-transparent mb-2">
                        ${typeof bestPrediction.prediction === 'number' ? bestPrediction.prediction.toFixed(2) : bestPrediction.prediction}
                      </div>
                      <p className="text-text-400 text-sm mb-4">Next 24h prediction</p>
                    </>
                  )}
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-background-700/50 rounded-lg">
                      <span className="text-text-400 text-sm">Confidence</span>
                      <span className="text-primary-400 font-medium">
                        {loading ? '--' : `${bestPrediction.confidence || 0}%`}
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-background-700/50 rounded-lg">
                      <span className="text-text-400 text-sm">Trend</span>
                      <span className={`font-medium ${
                        bestPrediction.trend === 'bullish' || bestPrediction.trend === 'up' 
                          ? 'text-green-400' 
                          : bestPrediction.trend === 'bearish' || bestPrediction.trend === 'down'
                          ? 'text-red-400'
                          : 'text-secondary-400'
                      }`}>
                        {loading ? '--' : (bestPrediction.trend || 'Neutral').toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Market Sentiment - Full Width */}
          <div className="lg:col-span-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-secondary-500/10 to-primary-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative p-6 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30 hover:border-secondary-500/30 transition-all duration-300">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-secondary-500/20 rounded-lg">
                    <Activity className="w-6 h-6 text-secondary-400" />
                  </div>
                  <h2 className="text-2xl font-semibold text-text-100">Market Sentiment</h2>
                  <div className="ml-auto px-3 py-1 bg-secondary-500/20 text-secondary-400 rounded-full text-sm font-medium">
                    Live Analysis
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-background-700/50 rounded-xl">
                    <div className="text-2xl font-bold text-accent-400 mb-1">
                      {loading ? '--' : metrics.bullishCount}
                    </div>
                    <div className="text-text-400 text-sm">Bullish Signals</div>
                  </div>
                  <div className="text-center p-4 bg-background-700/50 rounded-xl">
                    <div className="text-2xl font-bold text-primary-400 mb-1">
                      {loading ? '--' : `${metrics.avgConfidence}%`}
                    </div>
                    <div className="text-text-400 text-sm">Avg Confidence</div>
                  </div>
                  <div className="text-center p-4 bg-background-700/50 rounded-xl">
                    <div className="text-2xl font-bold text-secondary-400 mb-1">
                      {loading ? '--' : metrics.newsCount}
                    </div>
                    <div className="text-text-400 text-sm">News Articles</div>
                  </div>
                </div>
                
                {/* Individual Ticker Predictions */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                  {tickers.map(ticker => (
                    <div key={ticker} className="p-4 bg-background-700/30 rounded-xl">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-text-200">{ticker}</span>
                        <span className={`text-sm font-medium ${
                          loading ? 'text-text-400' :
                          (predictionsData[ticker]?.trend === 'bullish' || predictionsData[ticker]?.trend === 'up') 
                            ? 'text-green-400' 
                            : (predictionsData[ticker]?.trend === 'bearish' || predictionsData[ticker]?.trend === 'down')
                            ? 'text-red-400'
                            : 'text-yellow-400'
                        }`}>
                          {loading ? '--' : predictionsData[ticker]?.trend?.toUpperCase() || 'NEUTRAL'}
                        </span>
                      </div>
                      <div className="text-lg font-bold text-accent-400">
                        ${loading ? '--' : 
                          typeof predictionsData[ticker]?.prediction === 'number' 
                            ? predictionsData[ticker].prediction.toFixed(2) 
                            : predictionsData[ticker]?.prediction || '--'
                        }
                      </div>
                      <div className="text-sm text-text-400">
                        Confidence: {loading ? '--' : `${predictionsData[ticker]?.confidence || 0}%`}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-background-800/40 backdrop-blur-sm rounded-full border border-background-600/30">
            <span className="text-text-400">© 2025 StAI - Built with</span>
            <span className="text-accent-400">❤️</span>
            <span className="text-text-400">by</span>
            <span className="text-primary-400 font-medium">Amardeep</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Home;