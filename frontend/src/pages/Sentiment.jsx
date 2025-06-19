import axios from "axios";
import React, { useEffect, useState } from "react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import NewsCard from "../components/NewsCard";
const baseURL = import.meta.env.VITE_API_BASE_URL;
const COLORS = {
  positive: "#22c55e",
  neutral: "#facc15",
  negative: "#ef4444",
};

const Sentiment = () => {
  const [tickers, setTickers] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("AAPL");
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch ticker list on mount
  useEffect(() => {
    const fetchTickers = async () => {
      try {
        const res = await axios.get(`${baseURL}/tickers`);
        setTickers(res.data.tickers || []);
      } catch (err) {
        console.error("Failed to fetch ticker list:", err);
      }
    };

    fetchTickers();
  }, []);

  // Fetch sentiment for selected ticker
  useEffect(() => {
    const fetchSentiment = async () => {
      if (!selectedTicker) return;
      try {
        setLoading(true);
        const res = await axios.get(`${baseURL}/sentiment/${selectedTicker}`);
        setSentimentData(res.data);
        setError("");
      } catch (err) {
        console.error(err);
        setError("Failed to fetch sentiment data.");
        setSentimentData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchSentiment();
  }, [selectedTicker]);

  const pieData = sentimentData
    ? Object.entries(sentimentData.summary).map(([key, value]) => ({
        name: key,
        value,
        color: COLORS[key],
      }))
    : [];

  return (
    <div className="min-h-screen bg-background-950 text-text-100 p-6">
      <h1 className="text-3xl font-bold mb-6">Market Sentiment</h1>

      {/* Dropdown to select ticker */}
      <div className="mb-8">
        <label className="block mb-2 text-sm text-text-400">Select a Stock:</label>
        <select
          value={selectedTicker}
          onChange={(e) => setSelectedTicker(e.target.value)}
          className="bg-background-800 border border-background-600/30 text-text-100 rounded-lg p-2 focus:outline-none"
        >
          {tickers.map((ticker) => (
            <option key={ticker} value={ticker}>
              {ticker}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-text-400">Fetching sentiment...</p>
      ) : error ? (
        <p className="text-red-400">{error}</p>
      ) : sentimentData ? (
        <>
          {/* Donut Chart */}
          <div className="w-full max-w-xl mx-auto mb-8">
            <div className="bg-background-800/50 p-6 rounded-xl border border-background-600/30">
              <h2 className="text-xl font-semibold text-center mb-4">Sentiment Summary</h2>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    innerRadius={45}
                    label={({ name, percent }) =>
                      `${name} (${(percent * 100).toFixed(0)}%)`
                    }
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* News Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sentimentData.articles.map((article, idx) => (
              <NewsCard key={idx} article={article} />
            ))}
          </div>
        </>
      ) : (
        <p className="text-text-400">Select a stock to view sentiment analysis.</p>
      )}
    </div>
  );
};

export default Sentiment;
