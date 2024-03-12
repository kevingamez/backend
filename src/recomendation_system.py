from sqlalchemy.orm import Session
from models import Interaction, Song
from joblib import load

modelo = load('modelo_algo_cosine.joblib')

def get_song_recommendations(user_id: int, db: Session):
    all_songs = db.query(Song).all()

    user_interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
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