from flask import Blueprint, request, jsonify, abort
from flask_restful import Api, Resource
from uuid import uuid4
from datetime import datetime

from .models import db, Game  # Import SQLAlchemy a model Game

# Blueprint for API
api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')  # Nastavit url_prefix na /api/v1
api = Api(api_bp)

# In-memory data store
games = {}

# Helper function
def validate_game_data(data):
    required_fields = ["name", "difficulty", "board"]
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required fields.")
    if len(data["board"]) != 15 or any(len(row) != 15 for row in data["board"]):
        abort(422, description="Board must be 15x15.")

# Resources
class GameList(Resource):
    def get(self):
        """Get all games from database."""
        games = Game.query.all()
        return jsonify([{
            "uuid": game.uuid,
            "name": game.name,
            "difficulty": game.difficulty,
            "gameState": game.game_state,
            "board": game.board,
            "createdAt": game.created_at.isoformat(),
            "updatedAt": game.updated_at.isoformat()
        } for game in games])

    def post(self):
        """Create a new game."""
        data = request.get_json()
        validate_game_data(data)

        game_id = str(uuid4())
        game = Game(
            uuid=game_id,
            name=data["name"],
            difficulty=data["difficulty"],
            board=data["board"]
        )
        db.session.add(game)
        db.session.commit()

        return {
            "uuid": game.uuid,
            "name": game.name,
            "difficulty": game.difficulty,
            "gameState": game.game_state,
            "board": game.board,
            "createdAt": game.created_at.isoformat(),
            "updatedAt": game.updated_at.isoformat()
        }, 201

class GameDetail(Resource):
    def get(self, uuid):
        """Get a game by UUID."""
        game = Game.query.filter_by(uuid=uuid).first()
        if not game:
            abort(404, description="Game not found.")
        return {
            "uuid": game.uuid,
            "name": game.name,
            "difficulty": game.difficulty,
            "gameState": game.game_state,
            "board": game.board,
            "createdAt": game.created_at.isoformat(),
            "updatedAt": game.updated_at.isoformat()
        }

    def put(self, uuid):
        """Update a game by UUID."""
        game = Game.query.filter_by(uuid=uuid).first()
        if not game:
            abort(404, description="Game not found.")

        data = request.get_json()
        validate_game_data(data)

        game.name = data["name"]
        game.difficulty = data["difficulty"]
        game.board = data["board"]
        game.updated_at = datetime.utcnow()
        db.session.commit()

        return {
            "uuid": game.uuid,
            "name": game.name,
            "difficulty": game.difficulty,
            "gameState": game.game_state,
            "board": game.board,
            "createdAt": game.created_at.isoformat(),
            "updatedAt": game.updated_at.isoformat()
        }

    def delete(self, uuid):
        """Delete a game by UUID."""
        game = Game.query.filter_by(uuid=uuid).first()
        if not game:
            abort(404, description="Game not found.")

        db.session.delete(game)
        db.session.commit()
        return "", 204



# Add resources to API
api.add_resource(GameList, "/games")
api.add_resource(GameDetail, "/games/<string:uuid>")
