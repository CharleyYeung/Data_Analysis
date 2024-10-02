import pandas as pd
import numpy as np
from config.get_paths import load_analysis_paths,load_data_and_clusters, get_analysis_paths,  get_general_config
from config.analysis_functions import (
    calculate_trend, calculate_intra_cluster_correlations, calculate_correlations, calculate_volatility
)
from config.visualization_functions import (
    plot_trends, plot_trend_comparisons, plot_intra_cluster_correlations, plot_correlation_matrix, 
    plot_asset_volatility, plot_cluster_volatility
)

general_config = get_general_config()

# Load data and clustering results
all_data, optimal_labels = load_data_and_clusters()

# Extract asset names
assets = all_data.columns.tolist()

# Create clusters dictionary
clusters = {i: [asset for j, asset in enumerate(assets) if optimal_labels[j] == i] for i in set(optimal_labels)}

# Trend Analysis
for asset in assets:
    trend = calculate_trend(all_data[asset])
    print(f"Trend for {asset}: {trend}")
trends_plot = plot_trends(all_data, clusters)
trends_plot.savefig(load_analysis_paths('asset_and_cluster_trends.png'))
trends_plot.close()

trend_comparisons_plot = plot_trend_comparisons(all_data, all_data['yield_spread'])
trend_comparisons_plot.savefig(load_analysis_paths('trend_comparisons.png'))
trend_comparisons_plot.close()

# Overall Correlation Analysis
corr_matrix = calculate_correlations(all_data)
corr_matrix_plot = plot_correlation_matrix(corr_matrix)
corr_matrix_plot.savefig(load_analysis_paths('overall_correlation_matrix.png'))
corr_matrix_plot.close()

# Intra-Cluster Correlations
intra_cluster_corrs = {}
for cluster_name, cluster_assets in clusters.items():
    if len(cluster_assets) > 1:  # Only calculate for clusters with more than one asset
        intra_cluster_corrs[cluster_name] = calculate_intra_cluster_correlations(all_data, cluster_assets)

intra_cluster_plot = plot_intra_cluster_correlations(intra_cluster_corrs)
intra_cluster_plot.savefig(load_analysis_paths('intra_cluster_correlations.png'))
intra_cluster_plot.close()

    
print('All analytical graphs have been saved')