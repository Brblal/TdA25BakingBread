from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import JSON

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # Pokud Entry má cizí klíč na User, přidej to:
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Definování vztahu mezi Entry a User
    user = db.relationship('User', back_populates='entries')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(50))
    user_name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    
    entries = db.relationship('Entry')
    
    
    def get_id(self):
        return str(self.id)  # Flask-Login requires this method
    

    


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    game_state = db.Column(db.String(50), nullable=False)  # Např. "In Progress", "Game Over"
    current_player = db.Column(db.String(1), nullable=False)  # 'X' nebo 'O'
    board = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, difficulty, board=None, game_state='opening', uuid=None):
        self.name = name
        self.difficulty = difficulty
        self.uuid = uuid if uuid else str(func.uuid())  # Generates UUID if not provided
        self.board = board if board else [['' for _ in range(15)] for _ in range(15)]  # Default to 15x15 empty grid
        self.current_player = 'X'
        self.game_state = game_state



class Gamefp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    game_state = db.Column(db.String(50), default='opening')
    board = db.Column(db.PickleType, default=[['' for _ in range(15)] for _ in range(15)])
    player_x_uuid = db.Column(db.String(36), nullable=True)  # UUID pro hráče X
    player_o_uuid = db.Column(db.String(36), nullable=True)  # UUID pro hráče O
    current_player = db.Column(db.String(1), default='X')