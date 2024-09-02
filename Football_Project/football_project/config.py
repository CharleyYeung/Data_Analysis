import os

# Define the base directory
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the paths to the raw data files
league_table_raw_path = os.path.join(base_path, 'data', 'raw', 'league_table.csv')
player_in_raw_path = os.path.join(base_path, 'data', 'raw', 'player_transfer.csv')
player_out_raw_path = os.path.join(base_path, 'data', 'raw', 'player_transfer_out.csv')
total_passes_raw_path = os.path.join(base_path, 'data', 'raw', 'total_passes.csv')
transfer_data_raw_path = os.path.join(base_path, 'data', 'raw', 'transfer_data.csv')


# Define the path to the cleaned data directory
cleaned_data_path = os.path.join(base_path, 'data', 'cleaned')

# Define the paths to the cleaned data files for analysis
position_in_temp_path = os.path.join(base_path, 'data', 'cleaned', 'transferred_position_temp.csv')
league_table_temp_path = os.path.join(base_path, 'data', 'cleaned', 'league_table_temp.csv')
transfer_data_temp_path = os.path.join(base_path, 'data', 'cleaned', 'transfer_data_temp.csv')
combined_temp_path = os.path.join(base_path, 'data', 'cleaned', 'combined_temp.csv')
position_bal_temp_path = os.path.join(base_path, 'data', 'cleaned', 'transferred_positions_balance_temp.csv')
total_passes_temp_path = os.path.join(base_path, 'data', 'cleaned', 'total_passes_temp.csv')
position_out_temp_path = os.path.join(base_path, 'data', 'cleaned', 'transferred_position_out_temp.csv')
player_out_temp_path = os.path.join(base_path, 'data', 'cleaned', 'player_transfer_out_temp.csv')
player_in_temp_path = os.path.join(base_path, 'data', 'cleaned', 'player_transfer_temp.csv')
