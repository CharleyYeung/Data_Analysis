from fredapi import Fred
import yfinance as yf



def fred_scraping(api_key,ticker,start,end):
    fred = Fred(api_key)
    data = fred.get_series(ticker, observation_start=start, observation_end=end)
    df = data.reset_index()
    if df.empty:
        print('No data Downloaded')
    else:
        df.columns = ['Date', 'Close']
    return df


def yfinance_scraping(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    df = data['Close'].reset_index()
    if df.empty:
        print('No data Downloaded')
    else:
        df.columns = ['Date', 'Close']
    return df