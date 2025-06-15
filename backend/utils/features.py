import pandas as pd
import os

def get_features_for_ticker(ticker: str):
    path=f"../data/processed/{ticker}_processed.csv"
    if not os.path.exists(path):
        return None
    df=pd.read_csv(path)
    excluded_cols=["Date","Close","Target"]
    feature_cols=[col for col in df.columns if col not in excluded_cols]
    return feature_cols