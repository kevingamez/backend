from sqlalchemy.orm import Session
from models import Interactions, Item
from joblib import load

from surprise import Dataset, Reader
import pandas as pd

modelo = load('pearson.joblib')

def get_neighbors(k):
    neighbors_dict = {}
    for user_id_inner in modelo.trainset.all_users():
        neighbors_inner_ids = modelo.get_neighbors(user_id_inner, k)
        user_id_raw = modelo.trainset.to_raw_uid(user_id_inner)
        neighbors_raw_ids = [modelo.trainset.to_raw_uid(inner_id) for inner_id in neighbors_inner_ids]
        neighbors_dict[user_id_raw] = neighbors_raw_ids

    return neighbors_dict

def get_neighbors(user_id, k=10):
    df = pd.read_csv('/backend/csv-data/data.csv')
    print(user_id)
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['userid', 'traname', 'frecuencia']], reader)
    trainset = data.build_full_trainset()
    if not modelo.trainset:
        modelo.fit(trainset)
    inner_uid = trainset.to_inner_uid(user_id)
    neighbors = modelo.get_neighbors(inner_uid, k=k)
    neighbors_ids = [trainset.to_raw_uid(inner_id) for inner_id in neighbors]
    return neighbors_ids



def get_song_recommendations(mainstream_preferences):
    df = pd.read_csv('/backend/csv-data/data.csv')
    df = df[['userid', 'traname', 'frecuencia']]
    new_user_prefs = pd.DataFrame(mainstream_preferences)

    reader = Reader(rating_scale=(1, 5))  # Ajusta esto según tu escala de calificación
    updated_df = pd.concat([df, new_user_prefs]).reset_index(drop=True)

    # Carga el conjunto de datos actualizado
    data_updated = Dataset.load_from_df(updated_df[['userid', 'traname', 'frecuencia']], reader)
    trainset_updated = data_updated.build_full_trainset()

    predictions = []

    for item_inner_id in trainset_updated.all_items():
        item_raw_id = trainset_updated.to_raw_iid(item_inner_id)

        if item_raw_id not in new_user_prefs:
            prediction = modelo.predict(uid=None, iid=item_raw_id, r_ui=None, verbose=False)
            predictions.append((item_raw_id, prediction.est))
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    return predictions[:10]


