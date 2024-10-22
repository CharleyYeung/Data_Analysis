import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def calculate_trend(data):
    """Calculate the trend of a time series."""
    x = np.arange(len(data))
    return np.polyfit(x, data, 1)[0]

def calculate_correlations(data):
    """Calculate correlation matrix for all assets."""
    return data.corr()


def calculate_intra_cluster_correlations(data, cluster_assets):
    """Calculate correlations within a cluster."""
    return data[cluster_assets].corr()

def calculate_volatility(data, window):
    """Calculate rolling volatility of an asset."""
    log_returns = np.log(data / data.shift(1))
    return log_returns.rolling(window=window).std() * np.sqrt(window)