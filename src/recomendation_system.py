from sqlalchemy.orm import Session
from models import Interactions, Item
from joblib import load

from surprise import Dataset, Reader
import pandas as pd

modelo = load('pearson.joblib')

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

mainstream_preferences = [
    {'userid': 944, 'traname': 'Improvisation (Live_2009_4_15)', 'frecuencia': 1},
    {'userid': 944, 'traname': 'Glacier (Live_2009_4_15)', 'frecuencia': 1},
        {'userid': 944, 'traname': 'Parolibre (Live_2009_4_15)', 'frecuencia': 1},

    # Add more mainstream track preferences...
]
df = pd.read_csv('data.csv')

new_preferences_df = pd.DataFrame(mainstream_preferences)

reader = Reader(rating_scale=(1, 5))  # Ajusta esto según tu escala de calificación
updated_df = pd.concat([df, new_preferences_df]).reset_index(drop=True)

# Carga el conjunto de datos actualizado
data_updated = Dataset.load_from_df(updated_df[['userid', 'traname', 'frecuencia']], reader)
trainset_updated = data_updated.build_full_trainset()

def predict_for_new_user(new_user_prefs, model, trainset):
    # Crear una lista para almacenar las predicciones
    predictions = []

    # Iterar a través de todos los ítems en el conjunto de entrenamiento
    for item_inner_id in trainset.all_items():
        item_raw_id = trainset.to_raw_iid(item_inner_id)

        # Comprobar si el nuevo usuario ya ha interactuado con el ítem
        if item_raw_id not in new_user_prefs:
            # Predecir la calificación que el nuevo usuario podría dar al ítem
            # Como el usuario es nuevo, usamos None para el uid y luego establecemos test_uid a nuestro usuario ficticio
            prediction = model.predict(uid=None, iid=item_raw_id, r_ui=None, verbose=False)
            predictions.append((item_raw_id, prediction.est))

    # Ordenar las predicciones de mayor a menor estimación de calificación
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    return predictions

# Ejemplo de preferencias del nuevo usuario
new_user_prefs = {
    'Buzz Saw/Death By Catapult': 1,
    'Vaffanculo (Rock Version)': 1,
    'Sun Is Shining (Atb Mix)': 1,
    'English Breakfast': 1,
    'Electro Girl': 1,
    "I'M The Vanity": 1
}

# Predecir calificaciones para el nuevo usuario
new_user_predictions = predict_for_new_user(new_user_prefs, modelo, trainset_updated)

# Mostrar las top 10 recomendaciones para el nuevo usuario
print("Top 10 recommendations for the new user:")
for item, rating in new_user_predictions[:10]:
    print(f"{item}: {rating}")

