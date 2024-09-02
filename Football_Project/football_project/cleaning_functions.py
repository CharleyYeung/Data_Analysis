import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from football_project.get_paths import *
import pandas as pd
import numpy as np
import re
import yaml

path_config = get_yaml_path()



def total_passes_cleaning(passes):
    def year_organizing(df_passes):
        '''re-organizing data rows in total_passes.csv'''
        df_passes['Rank'] = df_passes['Rank'].astype(int)
        df_passes['Total Passes'] = df_passes['Total Passes'].str.replace(',', '', regex=False).astype(int)
        df_passes[['Year_start', 'Year_end']] = df_passes['Year'].str.split('/', expand=True).astype(int)
        df_passes.drop(columns=['Year', 'Year_end'], inplace=True)
        df_passes.rename(columns={'Year_start':'Year'}, inplace=True)
        return df_passes

    def passes_diff(df_passes):
        df_passes = df_passes.sort_values(['Club', 'Year'], ascending=[True, False])
        
        for club, group in df_passes.groupby('Club'):
            group['Total Passes Diff'] = group['Total Passes'].diff(-1)
            season_gaps = group['Year'].diff(-1).abs() > 1
            group.loc[season_gaps, 'Total Passes Diff'] = np.nan
            df_passes.loc[group.index, 'Total Passes Diff'] = group['Total Passes Diff']
        
        return df_passes

    passes = year_organizing(passes)
    passes = passes_diff(passes)
    return passes

def league_table_cleaning(league):

    league['Pts Diff'] = 0
    league['GF Diff'] = 0
    league['GA Diff'] = 0
    
    def goals_conversion(df_league):
        """
        Dealing with the column 'Goals': Separating Goal for and against from the column 'Goals'
        in league_table_temp.csv
        """
        
        try:

            """ Split using ':' instead of '/'"""

            df_league[['Goal For', 'Goal Against']] = df_league['Goals'].str.split(':', expand=True)
            df_league['Goal For'] = pd.to_numeric(df_league['Goal For'], errors='coerce')
            df_league['Goal Against'] = pd.to_numeric(df_league['Goal Against'], errors='coerce')
            
            df_league.drop(columns=['Goals'], inplace=True)
            print("Goals conversion successful")
        except Exception as e:
            print(f'Goal figure conversion failed: {str(e)}')
            print("First few rows of 'Goals' column:")
            print(df_league['Goals'].head())

        df_league = df_league[df_league['Year'] != 2024]

        if 'Goal For' in df_league.columns and 'Goal Against' in df_league.columns:
            print(df_league[['Goal For', 'Goal Against']].head())
        else:
            print("Error: 'Goal For' and/or 'Goal Against' columns were not created")

        return df_league
        print(df_league.head(5))
    
    def pt_diff(df_league):

        '''Create a new column for point difference'''

        df_league = df_league.sort_values(['Club', 'Year'], ascending=[True, False])

        for club, group in df_league.groupby('Club'):

            group['Pts Diff'] = -group['Pts'].diff()
            season_gaps = group['Year'].diff().abs() > 1
            group.loc[season_gaps, 'Pts Diff'] = np.nan
            df_league.loc[group.index, 'Pts Diff'] = group['Pts Diff']

        df_league = df_league.sort_values(['Club', 'Year'], ascending=[True, False])
        return df_league
    
    def goal_diff(df_league):

        '''Create two new columns for Goal for and Goal Against differences'''
        
        for club, group in df_league.groupby('Club'):
            # Calculate Goal For differences (GF Diff) for consecutive seasons
            group['GF Diff'] = group['Goal For'].diff()
            
            season_gaps = group['Year'].diff() > 1
            group.loc[season_gaps, 'GF Diff'] = np.nan
            df_league.loc[group.index, 'GF Diff'] = group['GF Diff']

        for club, group in df_league.groupby('Club'):
            # Calculate Goal Against difference (GA Diff) for consecutive seasons
            group['GA Diff'] = group['Goal Against'].diff()
            season_gaps = group['Year'].diff() > 1
            group.loc[season_gaps, 'GA Diff'] = np.nan
            df_league.loc[group.index, 'GA Diff'] = group['GA Diff']

        return df_league
    
    def table_arrangement(df_league):
        diff_columns = ['Pts Diff', 'GF Diff', 'GA Diff']
        for col in diff_columns:
            df_league[col] = df_league.groupby('Club')[col].shift(-1)
        df_league['GF Diff'] = -df_league['GF Diff']
        df_league['GA Diff'] = -df_league['GA Diff']
        new_order = ['Club', 'Game Played', 'W', 'D', 'L', '+/-', 'Year', 'Pts', 'Pts Diff','Goal For', 'GF Diff', 'Goal Against', 'GA Diff']
        df_league = df_league[new_order]
        df_league = df_league.sort_values(['Club', 'Year'], ascending=[True, False])
        return df_league

    league = goals_conversion(league)
    league = pt_diff(league)
    league = goal_diff(league)
    league = table_arrangement(league)
    return league
    

def transfer_data_process(df_money):

    def convert_balance(value):
        '''
        Converting the string format of the money balance of transfer window under the Balance 
        column in transfer_data_temp.csv
        '''

        if pd.isna(value):
            return None
        

        value = str(value).replace('€', '').replace(',', '')
        
        sign = -1 if value.startswith('-') else 1
        value = value.lstrip('-')
        

        match = re.match(r'(\d+\.?\d*)([kmb]?)', value.lower())
        if not match:
            return None
        
        number, suffix = match.groups()
        number = float(number)
        
        if suffix == 'm':
            return int(sign * number * 1_000_000)
        elif suffix == 'b':
            return int(sign * number * 1_000_000_000)
        elif suffix == 'k':
            return int(sign * number * 1_000)
        else:
            return int(sign * number)
        
    df_money['Balance'] = df_money['Balance'].apply(convert_balance)
    print("First few rows of 'Balance' after conversion:", df_money['Balance'].head())
    
    df_money = df_money.dropna(subset = ['Balance'])
    print("Number of rows after dropping NaN:", len(df_money))
    
    return df_money


def creating_balance_csv(in_temp, out_temp, in_ready, out_ready):
    temp_list = [in_temp, out_temp]
    ready_list = [in_ready, out_ready]
    mapping = dict(zip(temp_list, ready_list))
    
    def Calculate_position(file):



        input_path_player = get_preprocessed_file_paths(path_config['preprocessed_files'][file])


        player_data = pd.read_csv(input_path_player)
        df_player = pd.DataFrame(player_data)

        cleaned_folder = get_cleaned_folder_path('cleaned')
        ready_file = mapping[file]
        output_path = os.path.join(cleaned_folder, path_config['ready_files'][ready_file])

        positions = ['defender', 'forward', 'goalkeeper', 'midfielder']
        transfer_counts = {}

        for index, row in df_player.iterrows():
            club = row['Club']
            year = row['Year']
            position = row['Position']

            if club not in transfer_counts:
                transfer_counts[club] = {}
            if year not in transfer_counts[club]:
                transfer_counts[club][year] = {position: 0 for position in positions}
            
            if position in positions:
                transfer_counts[club][year][position] += 1

        result = []

        for club, years in transfer_counts.items():
            for year, counts in years.items():
                row = {'Club': club, 'Year': year}
                row.update(counts)
                result.append(row)

        result_df = pd.DataFrame(result)

        result_df = result_df.sort_values(by=['Club', 'Year'], ascending=[True, False])

        print(result_df)

        result_df.to_csv(output_path, index=False)
        print(f"Saved {file} dataframe to {output_path}")

    for file in temp_list:
        Calculate_position(file)


    df_in = pd.read_csv(get_cleaned_file_paths(path_config['ready_files']['position_in']))
    df_out = pd.read_csv(get_cleaned_file_paths(path_config['ready_files']['position_out']))
    output_path_balance = get_cleaned_file_paths(path_config['ready_files']['balance'])

    df_in.set_index(['Club', 'Year'], inplace=True)
    df_out.set_index(['Club', 'Year'], inplace=True)

    all_indexes = df_in.index.union(df_out.index)

    df_in = df_in.reindex(all_indexes, fill_value=0)
    df_out = df_out.reindex(all_indexes, fill_value=0)

    df_balance = df_in.sub(df_out)

    df_balance.sort_values(['Club', 'Year'], axis=0, ascending=[True, False], inplace=True)

    df_balance.reset_index(inplace=True)

    df_balance.to_csv(output_path_balance, index=False)

    print("Balance CSV file has been created successfully!")


