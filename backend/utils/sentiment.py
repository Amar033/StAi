import requests
import random
import os
from dotenv import load_dotenv
import joblib

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Get the current script directory (utils folder)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root (parent of utils)
project_root = os.path.dirname(script_dir)

# Load sentiment models with correct paths - models are inside utils/models
sentiment_model_path = os.path.join(script_dir, "models", "logistic_model.pkl")
vectorizer_path = os.path.join(script_dir, "models", "tfidf_vectorizer.pkl")

print(f"Looking for sentiment model at: {sentiment_model_path}")
print(f"Looking for vectorizer at: {vectorizer_path}")

try:
    sentiment_model = joblib.load(sentiment_model_path)
    vectorizer = joblib.load(vectorizer_path)
    print("Sentiment models loaded successfully!")
except FileNotFoundError as e:
    print(f"Warning: Could not load sentiment models - {e}")
    print("Please ensure the model files are in the utils/models/ directory")
    sentiment_model = None
    vectorizer = None

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
    
    # Crypto
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
}

def get_search_terms(ticker: str):
    """Generate search terms for better news retrieval"""
    clean_ticker = ticker.replace('.NS', '').replace('.BO', '').replace('^', '')
    
    if ticker in TICKER_MAPPING:
        name = TICKER_MAPPING[ticker]
        
        if ticker.startswith('^'):
            return [
                f'"{name}" index',
                f'{name} market',
                f'{name} today',
                name
            ]
        elif ticker.endswith('.NS') or ticker.endswith('.BO'):
            return [
                f'"{name}" stock',
                f'"{name}" India',
                f'{name} shares',
                clean_ticker
            ]
        else:
            return [
                f'"{name}" stock',
                f'{name} shares',
                f'{name} price',
                clean_ticker
            ]
    
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
    if not NEWS_API_KEY:
        print("Warning: NEWS_API_KEY not found in environment variables")
        return []
        
    search_terms = get_search_terms(ticker)
    all_articles = []
    
    for term in search_terms:
        url = (
            f"https://newsapi.org/v2/everything?q={term}&sortBy=publishedAt&pageSize={page_size}&language=en&apiKey={NEWS_API_KEY}"
        )
        
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                articles = r.json().get("articles", [])
                if articles:
                    all_articles.extend(articles)
                    break
            elif r.status_code == 429:
                print("API rate limit exceeded")
                break
            else:
                print(f"API request failed with status code: {r.status_code}")
        except requests.RequestException as e:
            print(f"Request failed for term '{term}': {e}")
            continue
    
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
    if not NEWS_API_KEY:
        return []
        
    search_terms = get_search_terms(ticker)
    articles = []
    
    # Try with Indian financial news sources
    indian_sources = "economic-times,the-times-of-india"
    
    for term in search_terms:
        # Try with Indian sources first
        url = (
            f"https://newsapi.org/v2/everything?q={term}&sources={indian_sources}&sortBy=publishedAt&pageSize={page_size}&apiKey={NEWS_API_KEY}"
        )
        
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                articles = r.json().get("articles", [])
                if articles:
                    break
        except requests.RequestException as e:
            print(f"Request failed for Indian sources: {e}")
            continue
        
        # If no results from Indian sources, try general search
        if not articles:
            url = (
                f"https://newsapi.org/v2/everything?q={term}&sortBy=publishedAt&pageSize={page_size}&language=en&apiKey={NEWS_API_KEY}"
            )
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    articles = r.json().get("articles", [])
                    if articles:
                        break
            except requests.RequestException as e:
                print(f"Request failed for general search: {e}")
                continue
    
    return articles

def analyze_sentiment(texts):
    """Analyze sentiment of text list"""
    if not texts:
        return []
        
    if sentiment_model is None or vectorizer is None:
        print("Warning: Sentiment models not loaded, returning neutral sentiment")
        return ["neutral"] * len(texts)
    
    try:
        # Clean and prepare texts
        clean_texts = [str(text).strip() for text in texts if text]
        if not clean_texts:
            return []
            
        x = vectorizer.transform(clean_texts)
        preds = sentiment_model.predict(x)
        return ["negative" if p == 0 else "positive" for p in preds]
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return ["neutral"] * len(texts)

def get_sentiment_for_ticker(ticker: str):
    """Get sentiment analysis for a ticker with improved Indian stock support"""
    print(f"Fetching sentiment for ticker: {ticker}")
    
    # Try both approaches
    articles = fetch_news(ticker)
    
    # If no articles found, try alternative approach
    if not articles:
        print("No articles found with primary method, trying alternative sources...")
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
    
    print(f"Analyzing sentiment for {len(headlines)} headlines...")
    sentiments = analyze_sentiment(headlines)
    
    summary = {
        "positive": sentiments.count('positive'),
        "neutral": sentiments.count('neutral'),
        "negative": sentiments.count('negative')
    }
    
    print(f"Sentiment summary: {summary}")
    
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

def add_ticker_mapping(ticker: str, name: str):
    """Add a new ticker to name mapping"""
    TICKER_MAPPING[ticker] = name
    print(f"Added mapping: {ticker} -> {name}")

# Test function to verify setup
def test_sentiment_setup():
    """Test if sentiment analysis is properly set up"""
    print("Testing sentiment analysis setup...")
    
    # Check if models are loaded
    if sentiment_model is None or vectorizer is None:
        print("❌ Sentiment models not loaded")
        return False
    
    # Test with sample text
    test_texts = ["This is great news!", "Market is falling badly"]
    try:
        sentiments = analyze_sentiment(test_texts)
        print(f"✅ Sentiment analysis working: {sentiments}")
        return True
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests when script is executed directly
    test_sentiment_setup()
    
    # Test with a sample ticker
    print("\nTesting with sample ticker...")
    result = get_sentiment_for_ticker("RELIANCE.NS")
    print(f"Result: {result}")