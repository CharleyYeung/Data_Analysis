from tslearn.clustering import TimeSeriesKMeans
from tslearn.clustering import silhouette_score as ts_silhouette_score
import numpy as np
import time
from tqdm import tqdm

def kmeans_clustering(data, n_clusters, metric, random_state=42):
    kmeans = TimeSeriesKMeans(n_clusters=n_clusters, metric=metric, random_state=random_state)
    labels = kmeans.fit_predict(data)
    return kmeans, labels


def calculate_silhouette_score(data, labels, metric):
    return ts_silhouette_score(data, labels, metric=metric)

def find_optimal_clusters(data, max_clusters, min_clusters, metric):
    silhouette_scores = []
    all_labels = []
    
    for n_clusters in tqdm(range(min_clusters, max_clusters + 1), desc="Calculating silhouette scores"):
        start_time = time.time()
        
        kmeans, labels = kmeans_clustering(data, n_clusters, metric)
        score = calculate_silhouette_score(data, labels, metric)
        print(f"Cluster labels: {labels}")
        
        silhouette_scores.append(score)
        all_labels.append(labels)
        
        end_time = time.time()
        print(f"Silhouette Score for {n_clusters} clusters: {score:.4f} (Time: {end_time - start_time:.2f} seconds)")
    
    optimal_index = silhouette_scores.index(max(silhouette_scores))
    optimal_clusters = optimal_index + min_clusters
    return optimal_clusters, silhouette_scores, all_labels, optimal_index

def print_cluster_assignments(labels, column_names):
    unique_labels = sorted(set(labels))
    for cluster in unique_labels:
        cluster_assets = [column_names[i] for i, label in enumerate(labels) if label == cluster]
        print(f"Cluster {cluster}: {', '.join(cluster_assets)}")