import polars as pl
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def analyze_driving_style(df: pl.DataFrame, n_clusters: int = 5) -> pl.DataFrame:
    # 1. feature engineering
    # mi calcolo l'accelerazione (derivata della velocità)
    # se manca questa, l'ai non capisce la differenza tra rettilineo e uscita curva
    df = df.with_columns([
        (pl.col("Speed").diff().fill_null(0) / 3.6 / 0.1).alias("Acc_Long_Approx")
    ])

    features = ["Speed", "Throttle", "Brake", "RPM", "Acc_Long_Approx"]

    # estraggo  la matrice numpy (gestisco i nan altrimenti sklearn esplode)
    data_matrix = df.select(features).to_numpy()
    data_matrix = np.nan_to_num(data_matrix) 

    # 2. scaling & clustering
    # scalo tutto: rpm arriva a 13k, freno è 0-1. senza scaler l'ai guarda solo i giri.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data_matrix)

    # faccio girare il k-means. n_init='auto' così fa veloce.
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(X_scaled)

    # 3. labeling intelligente (il ranking system)
    # invece di usare if brake > 0.5 (che se la media è 0.49 non va),
    # ordino i cluster in base alle caratteristiche fisiche.

    # riporto i centroidi alla scala originale per fare analisi
    centers = scaler.inverse_transform(kmeans.cluster_centers_)

    # mi creo una lista di dizionari per poterli ordinare facilmente
    cluster_stats = []
    for i, center in enumerate(centers):
        # indici: 0:Speed, 1:Throttle, 2:Brake, 3:RPM, 4:Acc
        cluster_stats.append({
            "id": i,
            "throttle": center[1],
            "brake": center[2],
            "acc": center[4],
            "speed": center[0],
            "label": None # questo lo riempio dopo
        })

    # strategia di assegnazione (vince il più forte):

    # A. quello con più gas medio è per forza il rettilineo (full gas)
    cluster_stats.sort(key=lambda x: x["throttle"], reverse=True)
    cluster_stats[0]["label"] = "5. Full Gas"

    # B. prendo quelli rimasti. quello con più freno è la staccata violenta.
    remaining = [c for c in cluster_stats if c["label"] is None]
    remaining.sort(key=lambda x: x["brake"], reverse=True)
    if remaining:
        remaining[0]["label"] = "1. Staccata"

    # C. il coasting è il più insidioso. è quello dove la somma di gas e freno è più bassa.
    # moltiplico freno * 100 per portarlo su scala 0-100 come il gas.
    remaining = [c for c in cluster_stats if c["label"] is None]
    remaining.sort(key=lambda x: x["throttle"] + (x["brake"] * 100), reverse=False) 
    if remaining:
        remaining[0]["label"] = "3. COASTING (Time Loss)"

    # D. tra quelli che avanzano, quello che accelera di più è l'uscita di curva
    remaining = [c for c in cluster_stats if c["label"] is None]
    remaining.sort(key=lambda x: x["acc"], reverse=True)
    if remaining:
        remaining[0]["label"] = "4. Uscita / Accelerazione"

    # E. l'ultimo che rimane è per forza il trail braking (fase mista/ingresso)
    remaining = [c for c in cluster_stats if c["label"] is None]
    if remaining:
        remaining[0]["label"] = "2. Trail Braking"

    # 4. mappatura finale
    # mi creo la mappa id -> nome e la applico
    label_map = {c["id"]: c["label"] for c in cluster_stats}

    final_labels = [label_map[c] for c in clusters]

    return df.with_columns(pl.Series("Driving_Phase", final_labels))