import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from config.visualization_functions import plot_elbow_from_scores, plot_silhouette
from config.preprocessing_functions import data_normalization
from config.get_paths import get_cleaned_paths, load_clustering, get_general_config
from config.clustering_functions import print_cluster_assignments

general_config = get_general_config()
clustering_metric = general_config['clustering']['metric']

# Load your data
all_data = pd.read_csv(get_cleaned_paths('all_data_cleaned.csv'))

# Normalize your data
normalization_columns = ['SP500', 'DJIA', 'NASDAQ', 'NIKKEI', 'HSI', 'SH', 'TWII', 'yield_spread']
all_data_normalized = all_data[normalization_columns]
all_data_normalized = data_normalization(all_data_normalized, normalization_columns)

# Load clustering results
clustering_results = load_clustering('clustering_results.npy')
optimal_n_clusters = clustering_results['optimal_n_clusters']
all_labels = clustering_results['all_labels']


# Reshape data for clustering (transpose the data)
reshaped_data = all_data_normalized.T.values

# Load clustering results
clustering_results = load_clustering('clustering_results.npy')
optimal_n_clusters = clustering_results['optimal_n_clusters']
silhouette_scores = clustering_results['silhouette_scores']
all_labels = clustering_results['all_labels']

# Calculate the optimal index
min_clusters = general_config['clustering']['n_clusters_range']['start']
optimal_index = optimal_n_clusters - min_clusters
optimal_labels = all_labels[optimal_index]

# Print cluster assignments
print("\nCluster Assignments:")
print_cluster_assignments(optimal_labels, normalization_columns)

# Print cluster assignments
print(f"\nOptimal number of clusters: {optimal_n_clusters}")
print(f"\nOptimal labels: {optimal_labels}")
print(f"\nLength of labels: {len(optimal_labels)}")



# Plot elbow curve using loaded silhouette scores
min_clusters = general_config['clustering']['n_clusters_range']['start']
elbow_plot = plot_elbow_from_scores(silhouette_scores, optimal_n_clusters, min_clusters)
elbow_plot.savefig(get_cleaned_paths('elbow_plot.png'))
plt.close()

# Plot silhouette for optimal number of clusters
optimal_labels = all_labels[optimal_n_clusters - min_clusters]  # Adjust index based on min_clusters
if len(np.unique(optimal_labels)) > 1:  # Only plot if there's more than one cluster
    # Use the reshaped data for silhouette plotting
    silhouette_data = reshaped_data
    silhouette_plot = plot_silhouette(silhouette_data, optimal_labels, optimal_n_clusters, metric=clustering_metric)
    silhouette_plot.savefig(get_cleaned_paths('silhouette_plot.png'))
    plt.close()
else:
    print("Cannot create silhouette plot: only one cluster in optimal solution.")

print("Elbow plot and Silhouette plot have been saved.")