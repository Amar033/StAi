import axios from 'axios';
import { AlertCircle, ArrowLeft, BarChart3, DollarSign, Pause, Play, RefreshCw } from "lucide-react";
import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import {
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

const SearchResults = () => {
    const { symbol } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    const [stockData, setStockData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [priceHistory, setPriceHistory] = useState([]);
    const [range, setRange] = useState(60); // default 60-day
    const [isAutoRefresh, setIsAutoRefresh] = useState(false);
    const [refreshInterval, setRefreshInterval] = useState(30); // seconds
    const [lastUpdated, setLastUpdated] = useState(null);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [sentiment,setSentiment]=useState("")
    
    const intervalRef = useRef(null);

    const fetchStockData = async (showLoading = true) => {
        try {
            if (showLoading) setLoading(true);
            setIsRefreshing(true);
            setError("");
            
            console.log(`Fetching data for symbol: ${symbol}`);

            const response = await axios.get(`http://127.0.0.1:8000/predict/${symbol}`, {
                timeout: 30000, // 30 second timeout
                headers: {
                    'Content-Type': 'application/json',
                },
                validateStatus: function (status) {
                    return status < 500;
                }
            });
            
            console.log('API Response:', response.data);
            
            if (response.status === 200 && response.data) {
                setStockData(response.data);
                setLastUpdated(new Date());
                
                // Fetch price history
                const historyRes = await axios.get(`http://127.0.0.1:8000/price-history/${symbol}?range=${range}`);
                setPriceHistory(historyRes.data.history);

                const sentimentRes = await fetch(`http://127.0.0.1:8000/sentiment/${symbol}`);
                const sentimentData = await sentimentRes.json();
                setSentiment(sentimentData);
                
                if (showLoading) setLoading(false);
            } else {
                throw new Error(`API returned status ${response.status}`);
            }
        } catch (err) {
            console.error('API Error:', err);
            
            let errorMessage = "Something went wrong while fetching data.";
            
            if (err.code === 'ECONNABORTED') {
                errorMessage = "Request timed out. Please try again.";
            } else if (err.response) {
                // Server responded with error status
                const status = err.response.status;
                const detail = err.response.data?.detail || err.response.data?.message;
                
                if (status === 404) {
                    errorMessage = `Model not found for ${symbol}. This stock might not be available for prediction.`;
                } else if (status === 400) {
                    errorMessage = detail || `Invalid request for ${symbol}.`;
                } else if (status === 500) {
                    errorMessage = detail || "Internal server error occurred.";
                } else {
                    errorMessage = detail || `Server error (${status})`;
                }
            } else if (err.request) {
                // Request was made but no response received
                errorMessage = "Cannot connect to the prediction server. Make sure the API is running on port 8000.";
            } else {
                // Something else happened
                errorMessage = err.message || "Unknown error occurred.";
            }
            
            setError(errorMessage);
            if (showLoading) setLoading(false);
        } finally {
            setIsRefreshing(false);
        }
    };

    // Manual refresh function
    const handleManualRefresh = () => {
        fetchStockData(false);
    };

    // Toggle auto refresh
    const toggleAutoRefresh = () => {
        setIsAutoRefresh(!isAutoRefresh);
    };

    // Check if market is open (simplified - you might want more sophisticated logic)
    const isMarketHours = () => {
        const now = new Date();
        const day = now.getDay(); // 0 = Sunday, 6 = Saturday
        const hour = now.getHours();
        
        // Basic market hours: Monday-Friday, 9:30 AM - 4:00 PM EST
        // This is simplified - you'd want to handle holidays, timezone conversions, etc.
        return day >= 1 && day <= 5 && hour >= 9 && hour < 16;
    };

    const formatLastUpdated = () => {
        if (!lastUpdated) return "Never";
        const now = new Date();
        const diffMs = now - lastUpdated;
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        
        if (diffSeconds < 60) {
            return `${diffSeconds} seconds ago`;
        } else if (diffMinutes < 60) {
            return `${diffMinutes} minutes ago`;
        } else {
            return lastUpdated.toLocaleTimeString();
        }
    };

    // Set up auto refresh interval
    useEffect(() => {
        if (isAutoRefresh && stockData) {
            intervalRef.current = setInterval(() => {
                fetchStockData(false);
            }, refreshInterval * 1000);
        } else {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        }

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [isAutoRefresh, refreshInterval, symbol]);

    // Initial data fetch and range change effect
    useEffect(() => {
        if (symbol) {
            fetchStockData(true);
        } else {
            setError("No symbol provided");
            setLoading(false);
        }

        // Cleanup interval on unmount
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [symbol, range]);

    if (loading) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-background-950 text-text-400">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-400 mb-4"></div>
                <p className="text-lg">Fetching data for {symbol?.toUpperCase()}...</p>
                <p className="text-sm text-text-500 mt-2">This may take a few moments</p>
            </div>
        );
    }
        
    if (error) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-background-950 text-red-400 p-6">
                <AlertCircle className="w-16 h-16 mb-4" />
                <h2 className="text-2xl font-bold mb-2">Error</h2>
                <p className="text-center mb-6 max-w-md">{error}</p>
                <div className="flex gap-4">
                    <button
                        onClick={() => navigate("/")}
                        className="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition"
                    >
                        Go Back Home
                    </button>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-3 bg-secondary-500 hover:bg-secondary-600 text-white rounded-lg transition"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    if (!stockData) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background-950 text-text-400">
                <p>No data available</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background-950 text-text-50 p-6">
            {/* Back Button */}
            <button
                onClick={() => navigate("/")}
                className="mb-6 inline-flex items-center gap-2 text-text-400 hover:text-primary-400 transition"
            >
                <ArrowLeft className="w-5 h-5" />
                Back to Home
            </button>

            {/* Stock Header with Refresh Controls */}
            <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-4xl font-bold text-primary-400">{stockData.symbol}</h1>
                    <p className="text-text-300 text-lg">{stockData.name}</p>
                    <p className="text-sm text-text-500">Last updated: {formatLastUpdated()}</p>
                </div>
                
                {/* Refresh Controls */}
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleManualRefresh}
                            disabled={isRefreshing}
                            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 text-white rounded-lg transition"
                        >
                            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                            Refresh
                        </button>
                        
                        <button
                            onClick={toggleAutoRefresh}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                                isAutoRefresh 
                                ? 'bg-green-600 hover:bg-green-700 text-white' 
                                : 'bg-gray-600 hover:bg-gray-700 text-white'
                            }`}
                        >
                            {isAutoRefresh ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                            Auto {isAutoRefresh ? 'ON' : 'OFF'}
                        </button>
                    </div>
                    
                    {/* Refresh Interval Selector */}
                    <div className="flex items-center gap-2 text-sm">
                        <span className="text-text-400">Update every:</span>
                        <select
                            value={refreshInterval}
                            onChange={(e) => setRefreshInterval(Number(e.target.value))}
                            className="bg-background-800 text-text-200 border border-background-600 rounded px-2 py-1"
                        >
                            <option value={15}>15 seconds</option>
                            <option value={30}>30 seconds</option>
                            <option value={60}>1 minute</option>
                            <option value={300}>5 minutes</option>
                        </select>
                    </div>
                    
                    {/* Market Status Indicator */}
                    {/* <div className="flex items-center gap-2 text-xs">
                        <div className={`w-2 h-2 rounded-full ${isMarketHours() ? 'bg-green-400' : 'bg-red-400'}`}></div>
                        <span className="text-text-500">
                            Market {isMarketHours() ? 'Open' : 'Closed'}
                        </span>
                    </div> */}
                </div>
            </div>

            {/* Overview Card */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
                <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
                    <p className="text-sm text-text-400">Current Price</p>
                    <p className="text-xl font-semibold text-accent-400">${stockData.price}</p>
                </div>
                <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
                    <p className="text-sm text-text-400">Change</p>
                    <p className={`text-xl font-semibold ${
                        stockData.change.includes('+') ? 'text-green-400' : 
                        stockData.change.includes('-') ? 'text-red-400' : 'text-primary-400'
                    }`}>
                        {stockData.change}
                    </p>
                </div>
                <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
                    <p className="text-sm text-text-400">Volume</p>
                    <p className="text-xl font-semibold text-secondary-400">{stockData.volume}</p>
                </div>
                <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
                    <p className="text-sm text-text-400">Sentiment</p>
                    <p className={`text-xl font-semibold ${
                        stockData.sentimentScore === 'Positive' ? 'text-green-400' :
                        stockData.sentimentScore === 'Negative' ? 'text-red-400' : 'text-accent-400'
                    }`}>
                        {stockData.sentimentScore}
                    </p>
                </div>
            </div>

            {/* Price Chart with Range Selector */}
            <div className="mb-10">
                <div className="p-6 bg-background-800/60 border border-background-600/30 rounded-2xl">
                    <div className="flex items-center gap-3 mb-4">
                        <BarChart3 className="text-primary-400 w-6 h-6" />
                        <h2 className="text-2xl font-semibold text-text-100">Price Chart</h2>
                    </div>
                    
                    {/* Range Selector */}
                    <div className="flex gap-2 mb-4">
                        {[30, 60, 360].map((r) => (
                            <button
                                key={r}
                                onClick={() => setRange(r)}
                                className={`px-3 py-1 rounded-lg text-sm ${
                                    range === r
                                        ? "bg-primary-500 text-white"
                                        : "bg-background-700 text-text-400 hover:bg-background-600"
                                }`}
                            >
                                Last {r}d
                            </button>
                        ))}
                    </div>

                    {/* Chart */}
                    <div className="h-64 bg-background-700/50 rounded-xl px-4 py-2">
                        {priceHistory.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={priceHistory}>
                                    <XAxis dataKey="date" stroke="#aaa" />
                                    <YAxis stroke="#aaa" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f1f1f', borderColor: '#444' }}
                                        labelStyle={{ color: '#ddd' }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="price"
                                        stroke="#34d399" // Tailwind green-400
                                        strokeWidth={2}
                                        dot={false}
                                        activeDot={{ r: 4 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <p className="text-center text-text-400 flex items-center justify-center h-full">Loading chart...</p>
                        )}
                    </div>
                </div>
            </div>

            {/* AI Prediction Card */}
            <div className="p-6 bg-background-800/60 border border-background-600/30 rounded-2xl">
                <div className="flex items-center gap-3 mb-4">
                    <DollarSign className="text-accent-400 w-6 h-6" />
                    <h2 className="text-2xl font-semibold text-text-100">AI Prediction</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                        <p className="text-sm text-text-400 mb-1">Predicted Price</p>
                        <p className="text-2xl font-bold text-accent-400">${stockData.prediction}</p>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-text-400 mb-1">Confidence</p>
                        <p className="text-2xl font-bold text-primary-400">{stockData.confidence}</p>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-text-400 mb-1">Trend</p>
                        <p className={`text-2xl font-bold ${
                            stockData.trend === 'Bullish' ? 'text-green-400' :
                            stockData.trend === 'Bearish' ? 'text-red-400' : 'text-secondary-400'
                        }`}>
                            {stockData.trend}
                        </p>
                    </div>
                </div>
            </div>

            {/* Technical Features Used (Debug Info) */}
            {stockData.features_used && (
                <div className="mt-8 p-6 bg-background-800/40 border border-background-600/20 rounded-2xl">
                    <h3 className="text-lg font-semibold text-text-200 mb-4">Technical Indicators Used</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                            <span className="text-text-400">Open: </span>
                            <span className="text-text-200">{stockData.features_used.open?.toFixed(2)}</span>
                        </div>
                        <div>
                            <span className="text-text-400">High: </span>
                            <span className="text-text-200">{stockData.features_used.high?.toFixed(2)}</span>
                        </div>
                        <div>
                            <span className="text-text-400">Low: </span>
                            <span className="text-text-200">{stockData.features_used.low?.toFixed(2)}</span>
                        </div>
                        <div>
                            <span className="text-text-400">Volume: </span>
                            <span className="text-text-200">{stockData.features_used.volume?.toLocaleString()}</span>
                        </div>
                        <div>
                            <span className="text-text-400">MA10: </span>
                            <span className="text-text-200">{stockData.features_used.ma10?.toFixed(2)}</span>
                        </div>
                        <div>
                            <span className="text-text-400">MA50: </span>
                            <span className="text-text-200">{stockData.features_used.ma50?.toFixed(2)}</span>
                        </div>
                        <div>
                            <span className="text-text-400">Returns: </span>
                            <span className="text-text-200">{(stockData.features_used.returns * 100)?.toFixed(2)}%</span>
                        </div>
                        <div>
                            <span className="text-text-400">Volatility: </span>
                            <span className="text-text-200">{(stockData.features_used.volatility * 100)?.toFixed(2)}%</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SearchResults;