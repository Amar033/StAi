import axios from 'axios';
import { ArrowLeft, BarChart3, DollarSign } from "lucide-react";
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';



const SearchResults = () => {
    const { symbol } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    const [stockData, setStockData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchStockData = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`http://127.0.0.1:8000/predict/${symbol}`);
                setStockData(response.data);
                setLoading(false);
            } catch (err) {
                console.error(err);
                setError("Something went wrong while fetching data.");
                setLoading(false);
            }
        };
    
        fetchStockData();
    }, [symbol]);
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background-950 text-text-400">
                Fetching data for {symbol}...
            </div>
            );
        }
        
        if (error) {
            return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-background-950 text-red-400">
                <p>{error}</p>
                <button
                onClick={() => navigate("/")}
                className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg"
                >
                Go Back
                </button>
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

      {/* Stock Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-primary-400">{stockData.symbol}</h1>
        <p className="text-text-300 text-lg">{stockData.name}</p>
      </div>
      {/* Overview Card */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
        <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
          <p className="text-sm text-text-400">Current Price</p>
          <p className="text-xl font-semibold text-accent-400">${stockData.price}</p>
        </div>
        <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
          <p className="text-sm text-text-400">Change</p>
          <p className="text-xl font-semibold text-primary-400">{stockData.change}</p>
        </div>
        <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
          <p className="text-sm text-text-400">Volume</p>
          <p className="text-xl font-semibold text-secondary-400">{stockData.volume}</p>
        </div>
        <div className="p-4 bg-background-800/60 border border-background-600/30 rounded-xl">
          <p className="text-sm text-text-400">Sentiment</p>
          <p className="text-xl font-semibold text-accent-400">{stockData.sentimentScore}</p>
        </div>
      </div>
            {/* Price Chart Placeholder */}
            <div className="mb-10">
        <div className="p-6 bg-background-800/60 border border-background-600/30 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            <BarChart3 className="text-primary-400 w-6 h-6" />
            <h2 className="text-2xl font-semibold text-text-100">Price Chart</h2>
          </div>
          <div className="h-64 flex items-center justify-center text-text-400 bg-background-700/50 rounded-xl">
            {/* Later: Replace with real chart */}
            Loading chart for {stockData.symbol}...
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
            <p className="text-2xl font-bold text-secondary-400">{stockData.trend}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchResults;
