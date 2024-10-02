import pandas as pd
import numpy as np
from config.get_paths import get_yaml_path, get_general_config, get_raw_paths
from config.scraping_functions import *
import yaml
import os

path_config = get_yaml_path()
general_config = get_general_config()
api_key = general_config['api_key']
tickers = general_config['ticker']
start = general_config['start']
end = general_config['end']



path_config = get_yaml_path()
general_config = get_general_config()

ticker_to_raw_map = {ticker: raw for ticker, raw in zip(path_config['raw'].keys(), general_config['ticker'].keys())}
for index_alias, ticker in general_config['ticker'].items():
    file_name = path_config['raw'][ticker_to_raw_map[index_alias]]
    file_path = get_raw_paths(file_name)
    try:
        print(f'Getting {file_name} data... from FRED'+'\n')
        data = fred_scraping(api_key, ticker, start, end)
        print(data.head())
    except Exception as e:
        print(f'Failed to get data from FRED: \n{e}.'+'\n' + f'Now getting {file_name} data from Yfinance!...'+'\n')
        data = yfinance_scraping(ticker,start,end)
        print(data.head())
    df = pd.DataFrame(data)
    try:
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f'{file_name} saved'+'\n')
    except Exception as e:
        print(f'Failed to save as {file_name}: {e}')

