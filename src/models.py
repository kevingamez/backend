from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
from database import Base
import enum
from pydantic import BaseModel
from sqlalchemy import ARRAY
from typing import List, Optional  # Importar List y Optional para el nuevo campo



class User(Base):
    __tablename__= 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    country = Column(String, nullable=True)
    
    
class Item(Base):
    __tablename__= 'songs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    

class RecomendationStatus(enum.Enum):
    positive = 'positive'
    negative = 'negative'
    undefined = 'None'
  

class Recomendation(Base):
    __tablename__= 'recomendations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('songs.id'))
    neighbors = Column(ARRAY(String), nullable=True) 
    status = Column(Enum(RecomendationStatus))
    
    
class Interactions(Base):
    __tablename__= 'interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('songs.id'))
    rating = Column(Float)
    
class UserResponse(BaseModel):
    id: int
    username: str
    country: Optional[str]
    
class ItemResponse(BaseModel):
    id: int
    title: str
    
class RecomendationResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    status: RecomendationStatus
    neighbors: Optional[List[str]] = None
    
class RecomendationUpdate(BaseModel):
    status: RecomendationStatus

    
class InteractionsResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    rating: float
    