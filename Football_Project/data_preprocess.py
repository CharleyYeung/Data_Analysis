from football_project.cleaning_functions import *
from football_project.get_paths import get_yaml_path, get_preprocessed_file_paths, get_cleaned_folder_path
import pandas as pd
import yaml
import os

path_config = get_yaml_path()

# total_passes_cleaning(df_passes)

ready_file = path_config['ready_files']['passes']
cleaned_folder = get_cleaned_folder_path('cleaned')
ready_file_path = os.path.join(cleaned_folder, ready_file)
input_path_passes = get_preprocessed_file_paths(path_config['preprocessed_files']['passes'])
passes_data = pd.read_csv(input_path_passes)
df_passes = pd.DataFrame(passes_data)

df_passes = total_passes_cleaning(df_passes)
print(df_passes.head())
df_passes.to_csv(ready_file_path, index=False)
print(f'{ready_file} is saved in the cleaned folder')


# league_table_process(df_league)


ready_file = path_config['ready_files']['league']
cleaned_folder = get_cleaned_folder_path('cleaned')
ready_file_path = os.path.join(cleaned_folder, ready_file)
input_path_league = get_preprocessed_file_paths(path_config['preprocessed_files']['league'])
league_data = pd.read_csv(input_path_league)
df_league = pd.DataFrame(league_data)

df_league = league_table_cleaning(df_league)

df_league.to_csv(ready_file_path, index=False)
print(f'{ready_file} is saved in the cleaned folder')



# transfer_data_cleaning(df_money)

try:
    ready_file = path_config['ready_files']['money']
    cleaned_folder = get_cleaned_folder_path('cleaned')
    ready_file_path = os.path.join(cleaned_folder, ready_file)
    input_path_money = get_preprocessed_file_paths(path_config['preprocessed_files']['money'])
    money_data = pd.read_csv(input_path_money)
    df_money = pd.DataFrame(money_data)

    transfer_data_process(df_money)
    
    df_money.to_csv(ready_file_path, index=False)
    print(f'{ready_file} is saved in the cleaned folder')
except Exception as e:
    print(f'{ready_file} !!!NOT!!! saved : {str(e)}')
    pass


# creating_balance_csv('player_in','player_out','position_in','position_out')

creating_balance_csv('player_in','player_out','position_in','position_out')


# Merge the two tables of league table and transfer data

ready_file = path_config['ready_files']['combined']
cleaned_folder = get_cleaned_folder_path('cleaned')
ready_file_path = os.path.join(cleaned_folder, ready_file)
league_data=pd.read_csv(get_cleaned_file_paths(path_config['ready_files']['league']))
df_league = pd.DataFrame(league_data)
money_data=pd.read_csv(get_cleaned_file_paths(path_config['ready_files']['money']))
df_money = pd.DataFrame(money_data)



df_combined = pd.merge(df_league, df_money,left_on=['Club', 'Year'],right_on=['Club', 'Year'],how='left')

df_combined = df_combined.sort_values(['Club', 'Year'], ascending=[True, False])

df_combined = df_combined.reset_index(drop=True)

print(df_combined.head())


df_combined['Balance'].replace(0, np.nan, inplace=True)

print(df_combined.iloc[[28,29,30,31,32],[11,12,13,14]])


df_combined.to_csv(ready_file_path, index=False)
print(f'{ready_file_path} is saved in the cleaned folder')