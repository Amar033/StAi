import React, { useState } from 'react';
import StockComparisonCard from '../components/StockComparisonCard';

const baseURL = import.meta.env.VITE_API_BASE_URL;
const StockForm = ({ onSubmit }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const symbols = input
      .toUpperCase()
      .replace(/\s/g, "")
      .split(",")
      .filter((s) => s.length > 0)
      .slice(0, 3);
    onSubmit(symbols);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6 flex gap-4 items-center">
      <input
        type="text"
        placeholder="Enter symbols (e.g., AAPL,GOOG,NVDA)"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="flex-1 p-3 rounded-lg bg-background-700 text-text-100 placeholder:text-text-500"
      />
      <button
        type="submit"
        className="px-4 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition"
      >
        Compare
      </button>
    </form>
  );
};

const Compare = () => {
  const [symbols, setSymbols] = useState([]);
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchData = async (symbolsList) => {
    setLoading(true);
    const newData = {};

    await Promise.all(
      symbolsList.map(async (symbol) => {
        try {
          const res = await fetch(`${baseURL}/predict/${symbol}`);
          const json = await res.json();
          newData[symbol] = json;
        } catch (e) {
          newData[symbol] = { error: true, message: e.message };
        }
      })
    );

    setData(newData);
    setLoading(false);
  };

  const handleSymbolsSubmit = (inputSymbols) => {
    setSymbols(inputSymbols);
    fetchData(inputSymbols);
  };

  return (
    <div className="min-h-screen bg-background-950 text-text-100 p-6">
      <h1 className="text-3xl font-bold mb-4">Compare Stocks</h1>

      {/* 🔍 Stock selection form */}
      <StockForm onSubmit={handleSymbolsSubmit} />

      {/* 📊 Results */}
      {loading ? (
        <p className="text-text-400">Fetching stock data...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {symbols.map((symbol) => (
            <StockComparisonCard key={symbol} symbol={symbol} stockData={data[symbol]} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Compare;
