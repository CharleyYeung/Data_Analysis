import os
import yaml
import numpy as np
import pandas as pd

def get_base_path():

    '''Get the paths of the root folder'''
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_path


def get_yaml_path():
    """Load the paths configuration from path_config.yaml."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'path_config.yaml')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def get_raw_paths(file):

    '''Get the paths of the raw csv files with the alias set in the 
    raw_file in the path_config.yaml file'''

    raw_path = os.path.join(get_base_path(), 'data', 'raw', file)
    return raw_path

def get_cleaned_paths(file):
    '''Get the paths of the cleaned csv files'''
    cleaned_path = os.path.join(get_base_path(), 'data', 'cleaned', file)
    return cleaned_path

def get_analysis_paths():
    '''Get the paths of the analysis files'''
    analysis_path = os.path.join(get_base_path(), 'data', 'analysis')
    return analysis_path

def load_analysis_paths(file):
    '''Get the paths of the analysis files'''
    analysis_path = os.path.join(get_base_path(), 'data', 'analysis',file)
    return analysis_path

def get_prediction_paths(file):
    '''Get the paths of the analysis files'''
    prediction_path = os.path.join(get_base_path(), 'data', 'prediction',file)
    return prediction_path

def get_general_config():

    '''Get the general configuration file'''
    config = get_yaml_path()
    general_config_path = os.path.join(os.path.dirname(__file__), config['general_config_files']['general_config'])
    with open(general_config_path, 'r') as file:
        return yaml.safe_load(file)
    
def load_clustering(file):
    clusters = np.load(get_cleaned_paths(file), allow_pickle=True).item()
    return clusters

def load_data_and_clusters():
    all_data = pd.read_csv(get_cleaned_paths('all_data_cleaned.csv'), index_col='Date')
    clustering_results = load_clustering('clustering_results.npy')
    optimal_labels = clustering_results['final_labels']
    return all_data, optimal_labels