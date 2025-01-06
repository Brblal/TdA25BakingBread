from flask import Blueprint, request, jsonify, abort
from flask_restful import Api, Resource
from uuid import uuid4
from datetime import datetime

# Blueprint for API
api_bp = Blueprint('api', __name__)
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
        """Get all games."""
        return jsonify(list(games.values()))

    def post(self):
        """Create a new game."""
        data = request.get_json()
        validate_game_data(data)

        game_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        game = {
            "uuid": game_id,
            "createdAt": now,
            "updatedAt": now,
            "name": data["name"],
            "difficulty": data["difficulty"],
            "gameState": "unknown",
            "board": data["board"],
        }
        games[game_id] = game
        return game, 201


class GameDetail(Resource):
    def get(self, uuid):
        """Get a game by UUID."""
        game = games.get(uuid)
        if not game:
            abort(404, description="Game not found.")
        return game

    def put(self, uuid):
        """Update a game by UUID."""
        if uuid not in games:
            abort(404, description="Game not found.")
        
        data = request.get_json()
        validate_game_data(data)

        game = games[uuid]
        game.update({
            "name": data["name"],
            "difficulty": data["difficulty"],
            "board": data["board"],
            "updatedAt": datetime.utcnow().isoformat(),
        })
        return game

    def delete(self, uuid):
        """Delete a game by UUID."""
        if uuid not in games:
            abort(404, description="Game not found.")
        del games[uuid]
        return "", 204


# Add resources to API
api.add_resource(GameList, "/games")
api.add_resource(GameDetail, "/games/<string:uuid>")
