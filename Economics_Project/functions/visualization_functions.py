import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from tslearn.clustering import silhouette_score
from tslearn.metrics import dtw
import matplotlib.dates as mdates

def plot_dtw_matrix(df):
    plt.figure(figsize=(10, 8))
    
    # Convert the dataframe to numeric values, replacing non-numeric with NaN
    numeric_df = df.apply(pd.to_numeric, errors='coerce')
    
    # Create a mask for NaN values
    mask = np.isnan(numeric_df)
    
    # Plot heatmap with mask
    sns.heatmap(numeric_df, cmap='YlOrRd', mask=mask, annot=True, fmt='.2f')
    plt.title('DTW Matrix Visualization')
    plt.xlabel('Time Series 2')
    plt.ylabel('Time Series 1')
    return plt
    print('Matrix plotted and saved in cleaned folder as "dtw_matrix.png"')

def silhouette_samples(X, labels, metric='dtw'):
    n_samples = len(X)
    unique_labels = np.unique(labels)
    
    # Compute pairwise distances
    distances = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(i+1, n_samples):
            if metric == 'dtw':
                dist = dtw(X[i], X[j])
            else:
                dist = np.linalg.norm(X[i] - X[j])
            distances[i, j] = distances[j, i] = dist
    
    silhouette_vals = np.zeros(n_samples)
    
    for i in range(n_samples):
        own_cluster = labels[i]
        own_cluster_distances = distances[i, labels == own_cluster]
        own_average_distance = np.mean(own_cluster_distances)
        
        silhouette_vals[i] = -1  # Initialize with worst silhouette
        for other_cluster in unique_labels:
            if other_cluster != own_cluster:
                other_cluster_distances = distances[i, labels == other_cluster]
                other_average_distance = np.mean(other_cluster_distances)
                silhouette_val = (other_average_distance - own_average_distance) / max(own_average_distance, other_average_distance)
                silhouette_vals[i] = max(silhouette_vals[i], silhouette_val)
    
    return silhouette_vals


def plot_silhouette(X, labels, n_clusters, metric):
    plt.figure(figsize=(10, 7))
    
    # Compute the silhouette scores
    if metric == 'dtw':
        distances = np.zeros((X.shape[0], X.shape[0]))
        for i in range(X.shape[0]):
            for j in range(i+1, X.shape[0]):
                distances[i, j] = distances[j, i] = dtw(X[i], X[j])
        silhouette_avg = silhouette_score(distances, labels, metric='precomputed')
        sample_silhouette_values = silhouette_samples(distances, labels, metric='precomputed')
    else:
        silhouette_avg = silhouette_score(X, labels, metric=metric)
        sample_silhouette_values = silhouette_samples(X, labels, metric=metric)

    y_lower = 10
    for i in range(n_clusters):
        ith_cluster_silhouette_values = sample_silhouette_values[labels == i]
        ith_cluster_silhouette_values.sort()
        
        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i
        
        color = plt.cm.nipy_spectral(float(i) / n_clusters)
        plt.fill_betweenx(np.arange(y_lower, y_upper),
                          0, ith_cluster_silhouette_values,
                          facecolor=color, edgecolor=color, alpha=0.7)
        
        plt.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
        y_lower = y_upper + 10
    
    plt.title("The silhouette plot for the various clusters.")
    plt.xlabel("The silhouette coefficient values")
    plt.ylabel("Cluster label")
    plt.axvline(x=silhouette_avg, color="red", linestyle="--")
    plt.yticks([])  # Clear the yaxis labels / ticks
    plt.xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
    
    return plt


def plot_elbow_from_scores(silhouette_scores, optimal_n_clusters, min_clusters):
    plt.figure(figsize=(10, 7))
    plt.plot(range(min_clusters, len(silhouette_scores) + min_clusters), silhouette_scores, 'bx-')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Silhouette Score')
    plt.title('Elbow Method using Silhouette Score')
    plt.axvline(x=optimal_n_clusters, color='r', linestyle='--', label=f'Optimal clusters: {optimal_n_clusters}')
    plt.legend()
    return plt


def plot_trends(data, clusters):
    n_plots = len(data.columns) + len(clusters)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 8 * n_rows))
    axes = axes.flatten()

    for i, asset in enumerate(data.columns):
        axes[i].plot(data.index, data[asset])
        axes[i].set_title(f'Trend of {asset}')
        axes[i].set_xlabel('Time')
        axes[i].set_ylabel('Value')

    for i, (cluster_name, cluster_assets) in enumerate(clusters.items()):
        cluster_data = data[cluster_assets].mean(axis=1)
        axes[i+len(data.columns)].plot(data.index, cluster_data)
        axes[i+len(data.columns)].set_title(f'Trend of Cluster {cluster_name}')
        axes[i+len(data.columns)].set_xlabel('Time')
        axes[i+len(data.columns)].set_ylabel('Value')

    for i in range(n_plots, len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    return plt

def plot_trend_comparisons(data, yield_spread):
    """Plot trend comparisons of each asset with yield spread."""
    n_assets = len(data.columns) - 1  # Subtract 1 to exclude yield_spread
    n_cols = 2
    n_rows = (n_assets + n_cols - 1) // n_cols  # Calculate number of rows needed

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 8 * n_rows))
    axes = axes.flatten()

    for i, asset in enumerate(data.columns):
        if asset != 'yield_spread':
            axes[i].plot(data.index, data[asset], label=asset)
            axes[i].plot(data.index, yield_spread, label='Yield Spread')
            axes[i].set_title(f'{asset} vs Yield Spread')
            axes[i].set_xlabel('Time')
            axes[i].set_ylabel('Value')
            axes[i].legend()

    # Remove any unused subplots
    for i in range(n_assets, len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    return plt

def plot_intra_cluster_correlations(corr_matrices):
    """Plot correlation heatmaps for intra-cluster correlations."""
    n_clusters = len(corr_matrices)
    fig, axes = plt.subplots(1, n_clusters, figsize=(8*n_clusters, 6))
    if n_clusters == 1:
        axes = [axes]

    for i, (cluster_name, corr_matrix) in enumerate(corr_matrices.items()):
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=axes[i])
        axes[i].set_title(f'Cluster {cluster_name} Correlations')

    plt.tight_layout()
    return plt

def plot_correlation_matrix(corr_matrix):
    """Plot correlation matrix heatmap for all assets."""
    n_assets = corr_matrix.shape[0]
    
    # Adjust figure size based on number of assets
    figsize = (max(8, n_assets * 0.8), max(6, n_assets * 0.7))
    
    plt.figure(figsize=figsize)
    
    # Create heatmap
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, 
                fmt='.2f', linewidths=0.5, square=True)
    
    # Adjust font size based on number of assets
    font_size = max(8, min(10, 200 // n_assets))
    plt.title('Correlation Matrix of All Assets', fontsize=font_size + 2)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    
    # Rotate x-axis labels if there are many assets
    if n_assets > 10:
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return plt


def plot_predictions(dates, y_pred, y_true, title):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, y_true, label='Actual')
    ax.plot(dates, y_pred, label='Predicted')
    ax.set_title(f'{title} - Actual vs Predicted')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.legend()

    # Set x-axis to show approximately 2 dates per year
    years = mdates.YearLocator(1)   # every year
    months = mdates.MonthLocator(interval=6)  # every 6 months
    years_fmt = mdates.DateFormatter('%Y')

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)

    # Format the coords message box
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

    # Rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    plt.tight_layout()
    return fig

def plot_future_predictions(historical_dates, historical_data, future_pred, title):
    # Convert historical_dates to datetime if they're not already
    if isinstance(historical_dates, pd.Index):
        if not isinstance(historical_dates[0], pd.Timestamp):
            historical_dates = pd.to_datetime(historical_dates)
    else:
        if not isinstance(historical_dates.iloc[0], pd.Timestamp):
            historical_dates = pd.to_datetime(historical_dates)
    
    future_dates = pd.date_range(start=historical_dates[-1] + pd.Timedelta(days=1), periods=len(future_pred))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(historical_dates, historical_data, label='Historical')
    ax.plot(future_dates, future_pred, label='Predicted')
    ax.set_title(f'{title} - Future Predictions')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig