# import requests
# import random
# import os
# from dotenv import load_dotenv
# import joblib

# load_dotenv()

# NEWS_API_KEY=os.getenv('NEWS_API_KEY')
# script_dir = os.path.dirname(os.path.abspath(__file__))
# sentiment_model = joblib.load(os.path.join(script_dir, "model", "logistic_model.pkl"))
# vectorizer = joblib.load(os.path.join(script_dir, "model", "tfidf_vectorizer.pkl"))


# def fetch_news(ticker:str , page_size=5):
#     url=(
#         f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&pageSize={page_size}&language=en&apiKey={NEWS_API_KEY}"
#     )
#     r= requests.get(url)
#     if r.status_code != 200:
#         return []
#     return r.json().get("articles",[])

# def analyze_sentiment(texts):
#     x=vectorizer.transform(texts)
#     preds=sentiment_model.predict(x)
#     return ["negative" if p==0 else "positive" for p in preds]

# def get_sentiment_for_ticker(ticker:str):
#     articles=fetch_news(ticker)
#     headlines=[a['title'] for a in articles]
#     sentiments=analyze_sentiment(headlines)
#     summary={
#         "positive":sentiments.count('positive'),
#         "neutral":sentiments.count('neutral'),
#         "negative":sentiments.count('negative')
#     }
#     return {
#         "ticker":ticker.upper(),
#         "summary":summary,
#         "articles":[
#             {
#                 "title":a["title"],
#                 "url":a.get("url"),
#                 "source":a["source"]["name"],
#                 "sentiment":s
#             }
#             for a,s in zip(articles,sentiments)
#         ]
#     }

import requests
import random
import os
from dotenv import load_dotenv
import joblib

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
script_dir = os.path.dirname(os.path.abspath(__file__))
sentiment_model = joblib.load(os.path.join(script_dir, "model", "logistic_model.pkl"))
vectorizer = joblib.load(os.path.join(script_dir, "model", "tfidf_vectorizer.pkl"))

# Stock ticker to company/index name mapping
TICKER_MAPPING = {
    # Indian Stocks
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "ICICIBANK.NS": "ICICI Bank",
    "BHARTIARTL.NS": "Bharti Airtel",
    "ITC.NS": "ITC Limited",
    "SBIN.NS": "State Bank of India",
    "LT.NS": "Larsen & Toubro",
    "HCLTECH.NS": "HCL Technologies",
    "ASIANPAINT.NS": "Asian Paints",
    "MARUTI.NS": "Maruti Suzuki",
    "BAJFINANCE.NS": "Bajaj Finance",
    "TITAN.NS": "Titan Company",
    "WIPRO.NS": "Wipro",
    "TECHM.NS": "Tech Mahindra",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "NESTLEIND.NS": "Nestle India",
    "POWERGRID.NS": "Power Grid Corporation",
    
    # Market Indices (with ^ prefix)
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "NASDAQ",
    "^RUT": "Russell 2000",
    "^VIX": "VIX volatility",
    "^TNX": "10-Year Treasury",
    "^NSEI": "NIFTY 50",
    "^BSESN": "BSE SENSEX",
    "^FTSE": "FTSE 100",
    "^GDAXI": "DAX",
    "^N225": "Nikkei 225",
    
    # Crypto (some platforms use different prefixes)
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    
    # Add more mappings as needed
}

def get_search_terms(ticker: str):
    """Generate search terms for better news retrieval"""
    # Clean ticker for search
    clean_ticker = ticker.replace('.NS', '').replace('.BO', '').replace('^', '')
    
    # Check if it's a known ticker/index
    if ticker in TICKER_MAPPING:
        name = TICKER_MAPPING[ticker]
        
        # Different search strategies for indices vs stocks
        if ticker.startswith('^'):
            # For market indices
            return [
                f'"{name}" index',
                f'{name} market',
                f'{name} today',
                name
            ]
        elif ticker.endswith('.NS') or ticker.endswith('.BO'):
            # For Indian stocks
            return [
                f'"{name}" stock',
                f'"{name}" India',
                f'{name} shares',
                clean_ticker
            ]
        else:
            # For other stocks/assets
            return [
                f'"{name}" stock',
                f'{name} shares',
                f'{name} price',
                clean_ticker
            ]
    
    # For unknown tickers, use generic search terms
    if ticker.startswith('^'):
        return [
            f'{clean_ticker} index',
            f'{clean_ticker} market',
            clean_ticker
        ]
    else:
        return [
            f'"{clean_ticker}" stock',
            f'{clean_ticker} shares',
            f'{clean_ticker} company',
            clean_ticker
        ]

def fetch_news(ticker: str, page_size=10):
    """Fetch news with improved search strategy"""
    search_terms = get_search_terms(ticker)
    all_articles = []
    
    # Try different search terms
    for term in search_terms:
        url = (
            f"https://newsapi.org/v2/everything?q={term}&sortBy=publishedAt&pageSize={page_size}&language=en&apiKey={NEWS_API_KEY}"
        )
        
        r = requests.get(url)
        if r.status_code == 200:
            articles = r.json().get("articles", [])
            if articles:
                all_articles.extend(articles)
                break  # Stop if we found articles with this search term
    
    # Remove duplicates based on title
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title = article.get('title', '')
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    return unique_articles[:page_size]

def fetch_news_alternative_sources(ticker: str, page_size=5):
    """Alternative approach using multiple news sources"""
    search_terms = get_search_terms(ticker)
    articles = []
    
    # Try with Indian financial news sources
    indian_sources = "economic-times,the-times-of-india"
    
    for term in search_terms:
        # Try with Indian sources first
        url = (
            f"https://newsapi.org/v2/everything?q={term}&sources={indian_sources}&sortBy=publishedAt&pageSize={page_size}&apiKey={NEWS_API_KEY}"
        )
        
        r = requests.get(url)
        if r.status_code == 200:
            articles = r.json().get("articles", [])
            if articles:
                break
        
        # If no results from Indian sources, try general search
        if not articles:
            url = (
                f"https://newsapi.org/v2/everything?q={term}&sortBy=publishedAt&pageSize={page_size}&language=en&apiKey={NEWS_API_KEY}"
            )
            r = requests.get(url)
            if r.status_code == 200:
                articles = r.json().get("articles", [])
                if articles:
                    break
    
    return articles

def analyze_sentiment(texts):
    """Analyze sentiment of text list"""
    if not texts:
        return []
    
    x = vectorizer.transform(texts)
    preds = sentiment_model.predict(x)
    return ["negative" if p == 0 else "positive" for p in preds]

def get_sentiment_for_ticker(ticker: str):
    """Get sentiment analysis for a ticker with improved Indian stock support"""
    # Try both approaches
    articles = fetch_news(ticker)
    
    # If no articles found, try alternative approach
    if not articles:
        articles = fetch_news_alternative_sources(ticker)
    
    # If still no articles, return empty result
    if not articles:
        return {
            "ticker": ticker.upper(),
            "summary": {
                "positive": 0,
                "neutral": 0,
                "negative": 0
            },
            "articles": [],
            "message": "No recent news articles found for this ticker"
        }
    
    headlines = [a.get('title', '') for a in articles if a.get('title')]
    
    if not headlines:
        return {
            "ticker": ticker.upper(),
            "summary": {
                "positive": 0,
                "neutral": 0,
                "negative": 0
            },
            "articles": [],
            "message": "No valid headlines found"
        }
    
    sentiments = analyze_sentiment(headlines)
    
    summary = {
        "positive": sentiments.count('positive'),
        "neutral": sentiments.count('neutral'),
        "negative": sentiments.count('negative')
    }
    
    return {
        "ticker": ticker.upper(),
        "summary": summary,
        "articles": [
            {
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "sentiment": s,
                "publishedAt": a.get("publishedAt", "")
            }
            for a, s in zip(articles, sentiments)
            if a.get("title")
        ]
    }

# Helper function to add new ticker mappings
def add_ticker_mapping(ticker: str, name: str):
    """Add a new ticker to name mapping"""
    TICKER_MAPPING[ticker] = name