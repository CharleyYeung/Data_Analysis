import pandas as pd
import numpy as np
from tslearn.metrics import dtw
from sklearn.preprocessing import MinMaxScaler

def yield_spread(long_term, short_term):
    return long_term - short_term

def data_normalization(df,columns):
    scaler = MinMaxScaler()
    data_normalized = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)
    if isinstance(df, np.ndarray):
        df = pd.DataFrame(df, columns, index=df.index)
    print('Data normalization completed')
    return data_normalized


def data_trimming(df,begin,end):
    df = df.iloc[begin:-end]
    return df

def interpolate_missing_values(df):
    df = df.interpolate(method='linear')
    print('Missing data handled with linear interpolation.')
    return df

def dtw_distance(df, time_series_columns):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing_cols = [col for col in time_series_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"The following columns are missing from the DataFrame: {missing_cols}")

    distance_matrix = pd.DataFrame(index=time_series_columns, columns=time_series_columns)

    for i, ts1_name in enumerate(time_series_columns):
        for j, ts2_name in enumerate(time_series_columns):
            if i >= j:  # Avoid redundant calculations
                continue
            ts1 = df[ts1_name].dropna().values
            ts2 = df[ts2_name].dropna().values
            if len(ts1) == 0 or len(ts2) == 0:
                distance_matrix.iloc[i, j] = distance_matrix.iloc[j, i] = np.nan
            else:
                distance = dtw(ts1, ts2)
                distance_matrix.iloc[i, j] = distance_matrix.iloc[j, i] = distance

    print("DTW distance calculation completed.")
    return distance_matrix

