import polars as pl
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def analyze_driving_style(df: pl.DataFrame, n_clusters: int = 5) -> pl.DataFrame:
    df = df.with_columns([
        (pl.col("Speed").diff().fill_null(0) / 3.6 / 0.1).alias("Acc_Long_Approx")
    ])


    features = ["Speed", "Throttle", "Brake", "RPM", "Acc_Long_Approx"]

    data_matrix = df.select(features).to_numpy()
    # in caso di possibili NaN, li vado a sostituire con 0
    data_matrix = np.nan_to_num(data_matrix) 


    # scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data_matrix)
    # clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto') # n_init specifica il numero di inizializzazioni, ossia quante volte l'algoritmo viene eseguito con centroidi iniziali diversi
    clusters = kmeans.fit_predict(X_scaled)

    # interpretazione dei cluster
    clusters_labels = {}
    centers = scaler.inverse_transform(kmeans.cluster_centers_)


    for i, center in enumerate(centers):
        # 0:Speed, 1:Throttle, 2:Brake, 3:RPM, 4:Acc
        avg_throttle = center[1]
        avg_brake = center[2]
        avg_acc = center[4]
        
        if avg_brake > 0.5:
            label = "1. Staccata violenta"
        elif avg_throttle > 85:
            label = "5. Full gas"
        elif avg_throttle > 10 and avg_acc > 0.5:
            label = "4. Uscita / Accelerazione"
        elif avg_brake > 0.1:
            label = "2. Trail braking"
        else:
            label = "3. COASTING (Time Loss)" 
            
        clusters_labels[i] = label

    final_labels = [clusters_labels[c] for c in clusters]
    
    # ritorno il dataframe con la nuova colonna "Driving_Phase"
    return df.with_columns(pl.Series("Driving_Phase", final_labels))