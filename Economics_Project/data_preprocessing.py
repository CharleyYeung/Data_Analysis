import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from functions.preprocessing_functions import *
from config.get_paths import get_yaml_path, get_general_config, get_raw_paths, get_cleaned_paths
from functions.visualization_functions import plot_dtw_matrix, plot_silhouette, plot_silhouette_scores
from functions.clustering_functions import find_optimal_clusters, kmeans_clustering, print_cluster_assignments

path_config = get_yaml_path()
general_config = get_general_config()
equity_assets = general_config['equity_asset']
raw_path = get_raw_paths

long_term = general_config['yield_spread']['long_term']
short_term = general_config['yield_spread']['short_term']
long_term_data = pd.read_csv(get_raw_paths(path_config['raw'][long_term]))
short_term_data = pd.read_csv(get_raw_paths(path_config['raw'][short_term]))
dfs={}

long_term_data.set_index('Date', inplace=True)
short_term_data.set_index('Date', inplace=True)

yield_spread = yield_spread(long_term_data,short_term_data)

for asset in equity_assets:
        file_name = path_config['raw'][asset]
        dfs[asset] = pd.read_csv(get_raw_paths(file_name))
        dfs[asset].set_index('Date', inplace = True)

all_data = pd.concat([df['Close'] for df in dfs.values()] + [yield_spread], axis=1)
all_data.columns = equity_assets + ['yield_spread']
all_data.sort_index(inplace = True)
print(all_data.info())
all_data.to_csv(os.path.join(get_raw_paths('all_data_raw.csv')))
print('All Asset prices data combined and saved in raw folder as "all_data_cleaned"')

# Data Normalization and Missing Value Handling
print(f'before normalisation: {all_data.head(20)} \n')
normalization_columns = equity_assets + ['yield_spread']
all_data = data_normalization(all_data, normalization_columns)
print(f'after normalization:  {all_data.head(20)} \n')
trim_begin = general_config['trimming']['begin']
trim_end = general_config['trimming']['end']
all_data = data_trimming(all_data,trim_begin,trim_end)
print(f'after trimming:  {all_data.head(20)} \n')
all_data = interpolate_missing_values(all_data)
print(f'after interpolation:  {all_data.head(20)}\n')
all_data.to_csv(os.path.join(get_cleaned_paths('all_data_cleaned.csv')))
print('Data cleaned and saved in cleaned folder as "all_data_cleaned"')

# DTW calculation
time_series_columns = equity_assets + ['yield_spread']
distance_matrix = dtw_distance(all_data, time_series_columns)
print(distance_matrix)
plot_dtw_matrix = plot_dtw_matrix(distance_matrix)
plot_dtw_matrix.savefig(get_cleaned_paths('dtw_matrix.png'))
plt.close()

# Find the optimal number of clusters
min_clusters = general_config['clustering']['n_clusters_range']['start']
max_clusters = general_config['clustering']['n_clusters_range']['end']
clustering_metric = general_config['clustering']['metric']
reshaped_data = all_data[time_series_columns].T.values
optimal_n_clusters, silhouette_scores, all_labels, optimal_index = find_optimal_clusters(reshaped_data, max_clusters, min_clusters, clustering_metric)
print(f"Optimal number of clusters: {optimal_n_clusters}")

# Perform final clustering with the optimal number of clusters
kmeans, optimal_labels = kmeans_clustering(reshaped_data, optimal_n_clusters, clustering_metric)

# Print cluster assignments
print("\nCluster Assignments:")
print_cluster_assignments(optimal_labels, time_series_columns)

# Save clustering results
np.save(get_cleaned_paths('clustering_results.npy'), {
    'optimal_n_clusters': optimal_n_clusters,
    'silhouette_scores': silhouette_scores,
    'all_labels': all_labels,
    'optimal_index': optimal_index,
    'final_labels': optimal_labels,
    'kmeans_model': kmeans
})

# Plot silhouette score curve
silhouette_plot = plot_silhouette_scores(silhouette_scores, optimal_n_clusters, min_clusters)
silhouette_plot.savefig(get_cleaned_paths('silhouette_score_curve.png'))
plt.close()

# Plot silhouette for optimal number of clusters
if len(np.unique(optimal_labels)) > 1:  # Only plot if there's more than one cluster
    silhouette_plot = plot_silhouette(reshaped_data, optimal_labels, optimal_n_clusters, metric=clustering_metric)
    silhouette_plot.savefig(get_cleaned_paths('silhouette_plot.png'))
    plt.close()
else:
    print("Cannot create silhouette plot: only one cluster in optimal solution.")

print("Silhouettes plot have been saved.")