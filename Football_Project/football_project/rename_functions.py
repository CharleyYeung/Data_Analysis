import yaml
import os
import pandas as pd


def get_club_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'clubname_config.yaml')

    with open(config_path, 'r') as f:
        club_config = yaml.safe_load(f)

    return club_config

def get_position_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'position_config.yaml')

    with open(config_path, 'r') as f:
        position_config = yaml.safe_load(f)

    return position_config



def rename_clubs(df_player, raw_files):
    '''Standardize the club names'''

    club_config = get_club_config()

    try:
        for club_name, alias in club_config['club_names'].items():
            if club_name != 'Wimbledon FC (- 2004)':
                df_player['Club'] = df_player['Club'].str.replace(club_name, alias, regex=True)
            else:
                df_player['Club'] = df_player['Club'].str.replace(club_name, alias, regex=False)
        return df_player['Club']
        print(f'{raw_files} "Club" rows renamed')
    except:
        print(f'{raw_files} "Club" rows !!NOT!! renamed')
        pass
    
    print('Club names standardized\n')

    
def rename_positions(df_player, raw_files):
    '''Standardize the position names in the 'Position' column'''

    position_config = get_position_config()

    if "Position" in df_player.columns:
        try:
            position_mapping = {}
            for category, aliases in position_config['position_names'].items():
                for alias in aliases:
                    position_mapping[alias] = category

            df_player['Position'] = df_player['Position'].replace(position_mapping)

            return df_player['Position']
        
            print(f'{raw_files} "Position" rows renamed')
            print(df_player['Position'].head(10))
        except Exception as e:
            print(f'{raw_files} "Position" rows !!NOT!! renamed str{e}')
            pass
    else:
        print(f'{raw_files} has no Position column')

    print('Club names standardized\n')

def rename_club_column(df_player,raw_files):
    if not 'Club' in df_player.columns:
        try:
            df_player.rename(columns={'Team':'Club','Club Name':'Club'}, inplace=True)
        except:
            print(f'{raw_files} column name "Club" renamed')
            pass
    else:
        print(f'{raw_files} has "Club" in column and no need to rename')
    
    return df_player

def rename_position_column(df_player, raw_files):
    if 'Pos' in df_player.columns:
        try:
            df_player.rename(columns={'Pos':'Position'},inplace=True)
            print(f'{raw_files}: Column name "Position" renamed')
        except:
            print(f'{raw_files} Column name "Position" !!NOT!! renamed')
            pass
    elif 'Position Name' in df_player:
        try:
            df_player.rename(columns={'Position Name':'Position'},inplace=True)
            print(f'{raw_files}: Column name "Position" renamed')
        except:
            print(f'{raw_files} Column name "Position" !!NOT!! renamed')
            pass
    else: print(f'{raw_files} has "Position" in column inplace or has no need to rename')
    
    if not 'Year' in df_player.columns:
        try:
            df_player.rename(columns={'Season':'Year'},inplace=True)
            print(f'{raw_files}: Column name "Year" renamed')
        except:
            print(f'{raw_files} Column name "Year" !!NOT!! renamed')
            pass
    else: print(f'{raw_files} has "Year" in column and no need to rename')
    return df_player