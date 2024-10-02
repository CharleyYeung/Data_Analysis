import yaml
import os
from sklearn.preprocessing import LabelEncoder
from pandas.tseries.offsets import MonthEnd, YearEnd
import pandas as pd
import numpy as np
import logging

def find_alias_for_ticker(ticker_dict, target_ticker):
    for alias, ticker in ticker_dict.items():
        if ticker == target_ticker:
            return alias
    return None

def fix_cluster_labels(clusters):
    le = LabelEncoder()
    return le.fit_transform(clusters)

def period_conversion(periods):
    offsets = []
    for period in periods:
        if period.endswith('M'):
            offsets.append(MonthEnd(int(period[:-1])))
        elif period.endswith('Y'):
            offsets.append(YearEnd(int(period[:-1])))
        else:
            raise ValueError(f"Unsupported period: {period}")
    return offsets

def set_date_index(df):
    if df.index.name != 'Date':
        if 'Date' in df.columns:
            df = df.set_index('Date')
        else:
            print("Warning: 'Date' column not found. Using existing index.")
    
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.index = pd.date_range(start=df.index[0], end=df.index[-1], freq='B')
    df.index.name = 'Date'
    return df

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)


def signed_log_transform(data):
    return np.sign(data) * np.log1p(np.abs(data))

def log_transform(data):
    return np.log1p(data - data.min() + 1)

def get_ticker_from_alias(alias, ticker_dict):
    print(f"Searching for alias: {alias}")
    print(f"Ticker dictionary: {ticker_dict}")
    for key, value in ticker_dict.items():
        if value == alias:
            print(f"Found match: {key} -> {value}")
            return key
    print(f"No match found for alias: {alias}")
    return None
