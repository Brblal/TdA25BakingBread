from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    board = db.Column(db.JSON, nullable=False)  # Hrací deska jako JSON
    game_state = db.Column(db.String(50), default="unknown")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
