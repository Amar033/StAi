import requests
import random
import os
from dotenv import load_dotenv
import joblib

load_dotenv()

NEWS_API_KEY=os.getenv('NEWS_API_KEY')
script_dir = os.path.dirname(os.path.abspath(__file__))
# sentiment_model=joblib.load("model/logistic_model.pkl")
# vectorizer=joblib.load("model/tfidf_vectorizer.pkl")
sentiment_model = joblib.load(os.path.join(script_dir, "model", "logistic_model.pkl"))
vectorizer = joblib.load(os.path.join(script_dir, "model", "tfidf_vectorizer.pkl"))


def fetch_news(ticker:str , page_size=5):
    url=(
        f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&pageSize={page_size}&language=en&apiKey={NEWS_API_KEY}"
    )
    r= requests.get(url)
    if r.status_code != 200:
        return []
    return r.json().get("articles",[])

def analyze_sentiment(texts):
    x=vectorizer.transform(texts)
    preds=sentiment_model.predict(x)
    return ["negative" if p==0 else "positive" for p in preds]

def get_sentiment_for_ticker(ticker:str):
    articles=fetch_news(ticker)
    headlines=[a['title'] for a in articles]
    sentiments=analyze_sentiment(headlines)
    summary={
        "positive":sentiments.count('positive'),
        "neutral":sentiments.count('neutral'),
        "negative":sentiments.count('negative')
    }
    return {
        "ticker":ticker.upper(),
        "summary":summary,
        "articles":[
            {
                "title":a["title"],
                "url":a.get("url"),
                "source":a["source"]["name"],
                "sentiment":s
            }
            for a,s in zip(articles,sentiments)
        ]
    }
