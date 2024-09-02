import yaml
import os

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

def get_preprocessed_file_paths(file):
    
    '''Get the paths of the preprocessed csv files with the alias set in the 
    preprocessed_file in the path_config.yaml file'''
    
    
    preprocessed_path = os.path.join(get_base_path(), 'data', 'preprocessed', file)
    return preprocessed_path

def get_base_path():

    '''Get the paths of the root folder'''
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_path

def get_preprocessed_folder_path(folder):

    '''Get the paths of the preprocessed data folder'''
    preprocessed_path = os.path.join(get_base_path(), 'data', folder)
    return preprocessed_path

def get_cleaned_folder_path(folder):

    '''Get the paths of the cleaned data folder'''
    cleaned_path =  os.path.join(get_base_path(), 'data', folder)
    return cleaned_path

def get_cleaned_file_paths(file):
    
    '''Get the paths of the cleaned csv files with the alias set in the 
    cleaned_file in the path_config.yaml file'''
    
    
    cleaned_path = os.path.join(get_base_path(), 'data', 'cleaned', file)
    return cleaned_path

def get_analysis_folder_path(folder):

    '''Get the paths of the cleaned data folder'''
    analysis_path =  os.path.join(get_base_path(), 'data', folder)
    return analysis_path

def get_general_config():

    '''Get the general configuration file'''
    config = get_yaml_path()
    general_config_path = os.path.join(os.path.dirname(__file__), config['general_config_files']['general_config'])
    with open(general_config_path, 'r') as file:
        return yaml.safe_load(file)