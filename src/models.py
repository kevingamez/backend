from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
from database import Base
import enum
from pydantic import BaseModel


class User(Base):
    __tablename__= 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    country = Column(String)
    
    
class Item(Base):
    __tablename__= 'songs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    

class RecomendationStatus(enum.Enum):
    positive = 'positive'
    negative = 'negative'
    undefined = None
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('songs.id'))

class Recomendation(Base):
    __tablename__= 'recomendations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('songs.id'))
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
    country: str
    
class ItemResponse(BaseModel):
    id: int
    title: str
    
class RecomendationResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    status: RecomendationStatus
    
class InteractionsResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    rating: float
    