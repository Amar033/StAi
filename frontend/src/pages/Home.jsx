import { Activity, BarChart3, DollarSign, Search, TrendingUp } from 'lucide-react';
import { default as React, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MiniChart from '../components/MiniChart';


const Home = () => {
const [searchQuery, setSearchQuery] = useState('');
const navigate = useNavigate();
const [trendingData, setTrendingData] = useState({});
useEffect(() => {
  const tickers = ["AAPL", "GOOGL", "TSLA"];

  const fetchAll = async () => {
    const res = {};
    for (let t of tickers) {
      const { data } = await axios.get(`http://localhost:8000/price-history/${t}`);
      res[t] = data;
    }
    setTrendingData(res);
  };

  fetchAll();
}, []);

const handleAnalyze = () => {
    if (searchQuery.trim()) {
    navigate(`/search/${searchQuery.trim().toUpperCase()}`);
    }
};
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
                    <h2 className="text-2xl font-semibold text-text-100">Price Chart</h2>
                  </div>
                  <div className="flex items-center gap-2 text-accent-400">
                    <TrendingUp className="w-5 h-5" />
                    <span className="text-sm font-medium">Real-time</span>
                  </div>
                </div>
                
                <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
  <MiniChart symbol="AAPL" />
  <MiniChart symbol="GOOGL" />
  <MiniChart symbol="TSLA" />
</div>


              </div>
            </div>
          </div>

          {/* Predicted Price Card */}
          <div className="group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-accent-500/10 to-secondary-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative p-6 bg-background-800/60 backdrop-blur-sm rounded-2xl border border-background-600/30 hover:border-accent-500/30 transition-all duration-300 h-full">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-accent-500/20 rounded-lg">
                    <DollarSign className="w-6 h-6 text-accent-400" />
                  </div>
                  <h2 className="text-xl font-semibold text-text-100">AI Prediction</h2>
                </div>
                
                <div className="text-center">
                  <div className="text-4xl font-bold bg-gradient-to-r from-accent-400 to-secondary-400 bg-clip-text text-transparent mb-2">
                    --
                  </div>
                  <p className="text-text-400 text-sm mb-4">Next 24h prediction</p>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-background-700/50 rounded-lg">
                      <span className="text-text-400 text-sm">Confidence</span>
                      <span className="text-primary-400 font-medium">--%</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-background-700/50 rounded-lg">
                      <span className="text-text-400 text-sm">Trend</span>
                      <span className="text-secondary-400 font-medium">--</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* News Sentiment - Full Width */}
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
                    <div className="text-2xl font-bold text-accent-400 mb-1">--</div>
                    <div className="text-text-400 text-sm">Bullish Signals</div>
                  </div>
                  <div className="text-center p-4 bg-background-700/50 rounded-xl">
                    <div className="text-2xl font-bold text-primary-400 mb-1">--</div>
                    <div className="text-text-400 text-sm">Overall Score</div>
                  </div>
                  <div className="text-center p-4 bg-background-700/50 rounded-xl">
                    <div className="text-2xl font-bold text-secondary-400 mb-1">--</div>
                    <div className="text-text-400 text-sm">News Impact</div>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-background-700/30 rounded-xl">
                  <p className="text-text-300 text-center">
                    Select a stock symbol to view real-time sentiment analysis and market insights
                  </p>
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