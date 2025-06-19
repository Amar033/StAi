import React, { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
const baseURL = import.meta.env.VITE_API_BASE_URL;
const MiniChart = ({ symbol }) => {
  const [priceHistory, setPriceHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${baseURL}/price-history/${symbol}?range=60`);
        const data = await res.json();
        setPriceHistory(data.history);
      } catch (err) {
        console.error("Error fetching chart data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [symbol]);

  return (
    <div className="h-64 bg-background-800/60 border border-background-600/30 rounded-xl px-4 py-2">
      <h3 className="text-lg text-text-100 font-semibold mb-2">{symbol} Price Chart</h3>
      {loading ? (
        <p className="text-text-400 text-sm">Loading...</p>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={priceHistory}>
            <XAxis dataKey="date" stroke="#aaa" hide />
            <YAxis stroke="#aaa" hide />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f1f1f', borderColor: '#444' }}
              labelStyle={{ color: '#ddd' }}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#34d399"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default MiniChart;
