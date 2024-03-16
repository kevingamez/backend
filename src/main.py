from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import models
from database import sessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import uvicorn
from pydantic import BaseModel
from typing import List, Annotated
import enum
from recomendation_system import get_song_recommendations

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)] 

class Item(BaseModel):
    title: str
    
class User(BaseModel):
    username: str
    password: str
    country: str
    
class RecomendationStatus(str, enum.Enum):
    positive = 'positive'
    negative = 'negative'
    undefined = None
    
class Recomendation(BaseModel):
    user_id: int
    item_id: int
    status: RecomendationStatus
    
class Interactions(BaseModel):
    user_id: int
    item_id: int
    rating: float

@app.get('/')
def read_root():
    return {'message': 'Hello World'}


@app.post('/signup/', response_model=models.UserResponse)
def signup(user: User, db: db_dependency):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = models.User(username=user.username, password=user.password, country=user.country)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  
    return models.UserResponse(id=db_user.id, username=db_user.username, country=db_user.country)


@app.post('/login/', response_model=models.UserResponse)
def login(user: User, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    if db_user.password != user.password:
        raise HTTPException(status_code=401, detail='Invalid password')
    return db_user

@app.get('/logout/')
def logout():
    return {'message': 'Logged out'}

@app.get('/users/', response_model=List[models.UserResponse])
def get_users(db: db_dependency):
    users = db.query(models.User).all()
    return users

@app.get('/users/{user_id}', response_model=models.UserResponse)
def get_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user

@app.post('/songs/', response_model=models.ItemResponse)
def create_item(item: Item, db: db_dependency):
    db_item = models.Item(title=item.title)
    db.add(db_item)
    db.commit()
    return db_item

@app.get('/songs/', response_model=List[models.ItemResponse])
def get_items(db: db_dependency):
    items = db.query(models.Item).all()
    return items

@app.get('/songs/{item_id}', response_model=models.ItemResponse)
def get_item(item_id: int, db: db_dependency):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return item

@app.post('/recomendations/', response_model=models.RecomendationResponse)
def create_recomendation(recomendation: Recomendation, db: db_dependency):
    db_recomendation = models.Recomendation(user_id=recomendation.user_id, item_id=recomendation.item_id, status=recomendation.status)
    db.add(db_recomendation)
    db.commit()
    return db_recomendation

@app.get('/recomendations/', response_model=List[models.RecomendationResponse])
def get_recomendations(db: db_dependency):
    recomendations = db.query(models.Recomendation).all()
    return recomendations

@app.get('/recomendations/{recomendation_id}', response_model=models.RecomendationResponse)
def get_recomendation(recomendation_id: int, db: db_dependency):
    recomendation = db.query(models.Recomendation).filter(models.Recomendation.id == recomendation_id).first()
    if recomendation is None:
        raise HTTPException(status_code=404, detail='Recomendation not found')
    return recomendation

@app.post('/interactions/', response_model=models.InteractionsResponse)
def create_interaction(interaction: Interactions, db: db_dependency):
    db_interaction = models.Interactions(user_id=interaction.user_id, item_id=interaction.item_id, rating=interaction.rating)
    db.add(db_interaction)
    db.commit()
    return db_interaction


@app.get('/interactions/', response_model=List[models.InteractionsResponse])
def get_interactions(db: db_dependency):
    interactions = db.query(models.Interactions).all()
    return interactions

@app.get('/interactions/{interaction_id}', response_model=models.InteractionsResponse)
def get_interaction(interaction_id: int, db: db_dependency):
    interaction = db.query(models.Interactions).filter(models.Interactions.id == interaction_id).first()
    if interaction is None:
        raise HTTPException(status_code=404, detail='Interaction not found')
    return interaction


@app.get('/user/{user_id}/recomendations/', response_model=List[models.RecomendationResponse])
def get_user_recomendations(user_id: int, db: db_dependency):
    recomendations = db.query(models.Recomendation).filter(models.Recomendation.user_id == user_id).all()
    return recomendations

@app.get('/user/{user_id}/interactions/', response_model=List[models.InteractionsResponse])
def get_user_interactions(user_id: int, db: db_dependency):
    interactions = db.query(models.Interactions).filter(models.Interactions.user_id == user_id).all()
    return interactions

@app.get('/songs/random/', response_model=List[models.ItemResponse])
def get_random_songs(db: db_dependency):
    random_songs = db.query(models.Item).order_by(func.random()).limit(10).all()
    return random_songs

@app.get('/user/{user_id}/recommendations/', response_model=List[models.ItemResponse])
def get_recommendations(user_id: int, db: db_dependency):
    
    interactions = db.query(models.Interactions).filter(models.Interactions.user_id == user_id).all()

    # Construir mainstream_preferences a partir de las interacciones
    mainstream_preferences = []
    for interaction in interactions:
        # Para cada interacción, encontrar el nombre de la canción correspondiente
        song = db.query(models.Item).filter(models.Item.id == interaction.item_id).first()
        if song:  # Asegurarse de que la canción existe
            preference = {
                'userid': user_id,
                'traname': song.title,
                'frecuencia': 1  # Asumiendo que la frecuencia es siempre 1 según tu requisito
            }
            mainstream_preferences.append(preference)
    print(mainstream_preferences)
    song_recommendations = get_song_recommendations(mainstream_preferences)

    # Crear y guardar las recomendaciones en la base de datos
    recommended_items = []
    for song_id, rating in song_recommendations:
        item = db.query(models.Item).filter(models.Item.title == song_id).first()
        print(item)
        if item is None:
            continue  

        # Aquí deberías usar models.Recomendation (SQLAlchemy) en lugar de Recomendation (Pydantic)
        recommendation = models.Recomendation(
            user_id=user_id,
            item_id=item.id,
            pred=rating,  # Asegúrate de que este campo existe y es correcto.
            status=models.RecomendationStatus.undefined  # Asegúrate de que este es el valor correcto según tu diseño.
        )
        
        db.add(recommendation)
        db.commit()
        
        recommended_items.append(models.ItemResponse(id=item.id, title=item.title))

    return recommended_items


@app.patch('/recommendations/{recommendation_id}', response_model=models.RecomendationResponse)
def update_recommendation_status(recommendation_id: int, recommendation_update: models.RecommendationUpdate, db: db_dependency):
    recommendation = db.query(models.Recomendation).filter(models.Recomendation.id == recommendation_id).first()

    if recommendation is None:
        raise HTTPException(status_code=404, detail='Recommendation not found')
    
    recommendation.status = recommendation_update.status
    db.commit()
    db.refresh(recommendation)
    
    return recommendation

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)