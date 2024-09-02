import pandas as pd
import numpy as np
from football_project.get_paths import get_yaml_path, get_general_config,get_cleaned_file_paths, get_cleaned_folder_path, get_analysis_folder_path


general_config = get_general_config()

def millions_formatter(x, pos):
    return f'{x/1e6:.0f}M'
def format_value(value):
    if abs(value) >= 1e9:
        return f"{value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.2f}K"
    else:
        return f"{value:.2f}"

def get_metric_description(metric, diff):
    if metric == 'Point':
        return 'gained' if diff > 0 else 'dropped'
    elif metric == 'GF':
        return 'gained' if diff > 0 else 'dropped'
    elif metric == 'GA':
        return 'increased' if diff > 0 else 'decreased'

def format_result(value, balance, diff, metric):
    if pd.isna(value) or np.isinf(value):
        return None
    
    prefix = "Avg income" if balance > 0 else "Avg spending"
    description = get_metric_description(metric, diff)
    
    formatted_value = format_value(abs(value))
    
    return f"{prefix} per {metric} {description}: {formatted_value}"

def analyze_club_scenarios(club_data, scenarios):
    for _, row in club_data.iterrows():
        balance = row['Balance']
        pts_diff = row['Pts Diff']
        gf_diff = row['GF Diff']
        ga_diff = row['GA Diff']

        # Points Difference scenarios
        if balance < 0 and pts_diff > 0:
            scenarios['Expensed, More League Points'] += 1
        elif balance > 0 and pts_diff > 0:
            scenarios['Gain in Market, More League Points'] += 1
        elif balance < 0 and pts_diff < 0:
            scenarios['Expensed, Less League Points'] += 1
        elif balance > 0 and pts_diff < 0:
            scenarios['Gain in Market, Less League Points'] += 1

        # Goals For Difference scenarios
        if balance < 0 and gf_diff > 0:
            scenarios['Expensed, More Goals Scored'] += 1
        elif balance > 0 and gf_diff > 0:
            scenarios['Gain in Market, More Goals Scored'] += 1
        elif balance < 0 and gf_diff < 0:
            scenarios['Expensed, Less Goals Scored'] += 1
        elif balance > 0 and gf_diff < 0:
            scenarios['Gain in Market, Less Goals Scored'] += 1

        # Goals Against Difference scenarios
        if balance < 0 and ga_diff > 0:
            scenarios['Expensed, More Goals Conceded'] += 1
        elif balance > 0 and ga_diff > 0:
            scenarios['Gain in Market, More Goals Conceded'] += 1
        elif balance < 0 and ga_diff < 0:
            scenarios['Expensed, Less Goals Conceded'] += 1
        elif balance > 0 and ga_diff < 0:
            scenarios['Gain in Market, Less Goals Conceded'] += 1

    return scenarios

# utils.py

def calculate_club_correlations(group, min_seasons):
    if len(group) >= min_seasons:
        corr = group[['forward', 'midfielder', 'defender_goalkeeper', 'GF Diff', 'GA Diff', 'Total Passes Diff']].corr()
        return pd.Series({
            'Goal for Incre. and Forward Transcaction': corr.loc['GF Diff', 'forward'],
            'Goal Against Decre. and Defence Transaction': corr.loc['GA Diff', 'defender_goalkeeper'],
            'Passes Changes and Midfielder Transaction': corr.loc['Total Passes Diff', 'midfielder']
        })
    else:
        return pd.Series({'Goal for Incre. and Forward Transcaction': np.nan, 'Goal Against Decre. and Defence Transaction': np.nan, 'Passes Changes and Midfielder Transaction': np.nan})