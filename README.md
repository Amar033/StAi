# 🧠 StAI — Stock AI Prediction & Insights Dashboard

**StAI (Stock AI)** is an advanced full-stack web application that combines AI-based price prediction, market sentiment analysis, and intelligent stock insights into a sleek, modern dashboard. Built with **FastAPI** and **React**, it delivers real-time data, machine learning forecasts, and curated news analysis — all in one platform.

> 🔮 Make smarter stock decisions with live insights and AI-powered predictions.

---

## 🌐 Live Demo

**Frontend:** [https://st-ai.vercel.app](https://st-ai.vercel.app)  
**Backend:** *Hosted on Railway (API accessed via Vite env config)*

---

## 🚀 Features

- 📊 Real-time **Stock Price Charts**
- 🤖 **AI-Powered Predictions** for next 24h
- 💡 Actionable **Investment Insights** (Bullish, Buy Opportunities, Underperforming)
- 📰 Live **News Sentiment Analysis**
- 🔍 Ticker **Search & Stock Comparison**
- 🎨 Sleek **Dark/Light UI** with Tailwind CSS
- 📦 Seamless **Frontend–Backend Integration**
- ⚙️ Environment Variable-Based Configuration

---

## 🏗️ Tech Stack

| Frontend                | Backend                   | Machine Learning & Tools |
|------------------------|---------------------------|---------------------------|
| React + Vite           | FastAPI (Python)          | XGBoost                   |
| TailwindCSS            | Uvicorn + CORS            | Scikit-learn              |
| Axios + Vite `.env`    | Pydantic + Routers        | Pandas, NumPy             |
| Recharts               | YFinance + News Parsing   | Custom-trained models     |
| Vercel (Deployment)    | Railway (Deployment)      |                           |

---

## 📁 Project Structure

StAI/
├── backend/
│ ├── main.py # FastAPI entry point
│ ├── routers/ # API routes (predict, compare, insights, etc.)
│ ├── models/ # Trained .pkl ML models + scalers
│ ├── utils/ # Feature engineering, sentiment scraping
│ └── requirements.txt # Backend dependencies
├── frontend/
│ ├── src/
│ │ ├── components/ # UI Components (MiniChart, InsightSection, etc.)
│ │ ├── pages/ # Home.jsx, SearchResults.jsx, Compare.jsx, etc.
│ │ ├── App.jsx # Main app routing
│ │ └── index.jsx # Vite entry
│ ├── public/ # Favicon, static assets
│ └── vite.config.js # Vite + environment setup


## 👨‍💻 Author
Amardeep
🔗 [LinkedIn](https://www.linkedin.com/in/amar033)


## ⚠️ Disclaimer
This project is for educational and research purposes only.
Not intended for real financial trading. Always consult a financial advisor.
