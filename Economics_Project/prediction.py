import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config.get_paths import load_data_and_clusters, get_prediction_paths
from functions.ML_functions import prepare_data, train_and_evaluate, predict_future, evaluate_model
from functions.visualization_functions import plot_predictions, plot_future_predictions

# Load data and clustering results
all_data, optimal_labels = load_data_and_clusters()

# Create clusters dictionary
assets = all_data.columns.tolist()
clusters = {i: [asset for j, asset in enumerate(assets) if optimal_labels[j] == i] for i in set(optimal_labels)}

# Perform ML for each asset
for asset in assets:
    X, y, scaler = prepare_data(all_data[asset], asset)
    model, y_pred, mse, r2 = train_and_evaluate(X, y)
    
    y_pred_inv = scaler.inverse_transform(y_pred.reshape(-1, 1)).flatten()
    y_true_inv = all_data[asset].iloc[-len(y_pred):].values
    
    mae, mse, rmse, mape = evaluate_model(y_true_inv, y_pred_inv)
    
    fig = plot_predictions(all_data.index[-len(y_pred):], y_pred_inv, y_true_inv, asset)
    fig.savefig(get_prediction_paths(f'{asset}_predictions.png'))
    plt.close(fig)
    
    future_pred = predict_future(model, X[-1], scaler)
    fig = plot_future_predictions(all_data.index[-60:], all_data[asset].iloc[-60:], future_pred, asset)
    fig.savefig(get_prediction_paths(f'{asset}_future_predictions.png'))
    plt.close(fig)
    
    print(f"{asset} - MAE: {mae:.4f}, MSE: {mse:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%, R2: {r2:.4f}")

# Perform ML for each cluster
for cluster_id, cluster_assets in clusters.items():
    cluster_data = all_data[cluster_assets]
    cluster_mean = cluster_data.mean(axis=1)
    
    X, y, scaler = prepare_data(pd.DataFrame(cluster_mean), 'cluster_mean')
    model, y_pred, mse, r2 = train_and_evaluate(X, y)
    
    fig = plot_predictions(cluster_data.index[-len(y_pred):], y_pred, cluster_mean.iloc[-len(y_pred):], f'Cluster {cluster_id}')
    fig.savefig(get_prediction_paths(f'cluster_{cluster_id}_predictions.png'))
    plt.close(fig)
    
    future_pred = predict_future(model, X[-1], scaler)
    fig = plot_future_predictions(cluster_data.index[-60:], cluster_mean.iloc[-60:], future_pred, f'Cluster {cluster_id}')
    fig.savefig(get_prediction_paths(f'cluster_{cluster_id}_future_predictions.png'))
    plt.close(fig)
    
    print(f"Cluster {cluster_id} - MSE: {mse:.4f}, R2: {r2:.4f}")