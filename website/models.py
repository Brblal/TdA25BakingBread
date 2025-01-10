from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


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