import axios from 'axios';
import React, { useEffect, useState } from 'react';

const InsightCard = ({ title, tickers, color }) => (
  <div className={`p-4 rounded-xl shadow-lg bg-background-800/60 border-l-4 ${color} mb-6`}>
    <h3 className="text-xl font-semibold mb-2">{title}</h3>
    {tickers.length === 0 ? (
      <p className="text-text-400">No data available</p>
    ) : (
      <ul className="text-text-100 space-y-1">
        {tickers.map(t => (
          <li key={t}>• {t}</li>
        ))}
      </ul>
    )}
  </div>
);

const Insights = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get("http://localhost:8000/insights")
      .then(res => {
        setInsights(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-background-950 text-text-100 p-6">
      <h1 className="text-3xl font-bold mb-2">Investment Insights</h1>
      <p className="text-text-400 mb-8">AI-generated tips based on market trends</p>

      {loading ? (
        <p className="text-text-500">Loading insights...</p>
      ) : (
        <div className="grid md:grid-cols-2 gap-8">
          <InsightCard title="🔼 Top Bullish Stocks" tickers={insights.top_bullish} color="border-green-400" />
          <InsightCard title="🟢 Potential Buys" tickers={insights.potential_buys} color="border-blue-400" />
          <InsightCard title="🔻 Underperforming Stocks" tickers={insights.underperforming} color="border-red-400" />
        </div>
      )}
    </div>
  );
};

export default Insights;
