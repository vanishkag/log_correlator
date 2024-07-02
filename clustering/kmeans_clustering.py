from sklearn.cluster import KMeans

num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters)
log_df['cluster'] = kmeans.fit_predict(np.array(log_df['embedding'].tolist()))