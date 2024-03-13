from sqlalchemy.orm import Session
from models import Interactions, Item
from joblib import load

modelo = load('modelo_algo_cosine.joblib')

def get_song_recommendations(user_id: int, db: Session):
    all_songs = db.query(Item).all()

    user_interactions = db.query(Interactions).filter(Interactions.user_id == user_id).all()
    user_known_songs = [interaction.item_id for interaction in user_interactions]

    predictions = []

    for song in all_songs:
        if song.id not in user_known_songs:
            prediction = modelo.predict(user_id, song.id, r_ui=1.0)
            predictions.append((song.title, prediction.est))

    predictions.sort(key=lambda x: x[1], reverse=True)

    N = 10
    top_recommendations = predictions[:N]

    return top_recommendations


def get_neighbors(k):
    neighbors_dict = {}
    for user_id_inner in modelo.trainset.all_users():
        neighbors_inner_ids = modelo.get_neighbors(user_id_inner, k)
        user_id_raw = modelo.trainset.to_raw_uid(user_id_inner)
        neighbors_raw_ids = [modelo.trainset.to_raw_uid(inner_id) for inner_id in neighbors_inner_ids]
        neighbors_dict[user_id_raw] = neighbors_raw_ids

    return neighbors_dict
