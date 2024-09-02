from football_project.rename_functions import *
from football_project.get_paths import get_yaml_path, get_raw_paths, get_preprocessed_folder_path
import pandas as pd
import yaml
import os

path_config = get_yaml_path()
raw_to_temp_map = {raw: temp for raw, temp in zip(path_config['raw_files'].keys(), path_config['preprocessed_files'].keys())}

print(rename_clubs.__doc__+'\n')

print(rename_positions.__doc__+'\n')

for file_alias, raw_files in path_config['raw_files'].items():

    raw_path = get_raw_paths(raw_files)
    player_data = pd.read_csv(raw_path)
    df_player = pd.DataFrame(player_data)

    rename_club_column(df_player,raw_files)

    rename_position_column(df_player, raw_files)
        
    rename_clubs(df_player, raw_files)

    rename_positions(df_player, raw_files)

    try:
        df_player = df_player.sort_values(['Club','Year'],ascending=[True,False])
        print(f'{raw_files} data sorted')
    except:
        print(f'{raw_files} data !!NOT!! sorted')
        pass

    try:
        temp_file = path_config['preprocessed_files'][raw_to_temp_map[file_alias]]
        preprocessed_folder = get_preprocessed_folder_path('preprocessed')
        temp_file_path = os.path.join(preprocessed_folder, temp_file)
        
        df_player.to_csv(temp_file_path, index=False)
        print(f'{temp_file} is saved in the preprocessed folder')
    except Exception as e:
        print(f'{temp_file} !!!NOT!!! saved : {str(e)}')
        pass



print('File renaming preprocession Done\n')
