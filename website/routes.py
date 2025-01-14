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
    flattened_board = [cell for row in data["board"] for cell in row]
    x_count = flattened_board.count('X')
    o_count = flattened_board.count('O')
    if not all(cell in ['X', 'O', ''] for cell in flattened_board):
        abort(422, description="Board contains invalid characters. Only 'X', 'O', and '' are allowed.")
    # Validate move counts
    if not (x_count == o_count or x_count == o_count + 1):
        abort(422, description="Invalid game state: Incorrect counts of X and O.")
        

def compute_game_state(board):
    """Analyze the board and determine the game state."""
    
    # Flatten the board and count 'X' and 'O' symbols
    flattened_board = [cell for row in board for cell in row]
    x_count = flattened_board.count('X')
    o_count = flattened_board.count('O')

    # Determine state based on move count (Opening or Midgame)
    total_moves = x_count + o_count
    if total_moves < 6:
        return "opening"

    # Check for Endgame conditions (4 consecutive X's or O's)
    def check_line(line):
        count = 1
        for i in range(1, len(line)):
            if line[i] == line[i - 1] and line[i] in ['X', 'O']:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 1
        return False

    # Check rows for a winning condition
    for row in board:
        if check_line(row):
            return "endgame"

    # Check columns for a winning condition
    for col in range(len(board[0])):
        column = [board[row][col] for row in range(len(board))]
        if check_line(column):
            return "endgame"

    # Check diagonals for a winning condition
    for d in range(-len(board) + 1, len(board[0])):
        diagonal1 = [board[i][i + d] for i in range(max(0, -d), min(len(board), len(board[0]) - d))]
        diagonal2 = [board[i][len(board[0]) - 1 - i - d] for i in range(max(0, -d), min(len(board), len(board[0]) - d))]
        if check_line(diagonal1) or check_line(diagonal2):
            return "endgame"

    # If the game is still possible, it's Midgame (there are still empty cells)
    if "" in flattened_board:
        return "midgame"

    # If no empty cells and no winner, it's a draw
    return "draw"
        
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

    # Compute the game state
        game_state = compute_game_state(data["board"])

        game_id = str(uuid4())
        game = Game(
            uuid=game_id,
            name=data["name"],
            difficulty=data["difficulty"],
            board=data["board"],
            game_state=game_state  # Uložit stav hry
        )
        db.session.add(game)
        db.session.commit()

        return {
            "uuid": game.uuid,
            "name": game.name,
            "difficulty": game.difficulty,
            "gameState": game.game_state,  # Odpověď obsahuje stav hry
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
