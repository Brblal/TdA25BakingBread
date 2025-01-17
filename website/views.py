from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask import Flask
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import shutil
from . import db, create_app
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from base64 import b64encode
import json
import codecs


from flask import abort



views = Blueprint('views', __name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['UPLOAD_FOLDER'] = 'static/files'

api = Blueprint('api', __name__)




@views.route('/', methods=['GET', 'POST'])
def home():
    
    
  
    return render_template("home.html")
@views.route('/restart', methods=['GET', 'POST'])
def clear():
    game.reset_board();
    game.current_player = 'X'
    return jsonify({'status': 'success'})

@views.route('/make_move', methods=['GET', 'POST'])
def make_move():
    data = request.get_json()
    position = data['position']
    if game.make_move(position):
        winner = game.check_winner() 
        winning_combination = game.get_winning_combination()
        return jsonify({'status': 'success', 'winner': winner, 'board': game.board, 'winning_combination': winning_combination})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid move'})



  
    

@views.route('/game', methods=['GET', 'POST'])
def game():

  
    return render_template("game.html", board = game.board)

class TicTacToe:
    def __init__(self, size=15, win_condition=5):
        self.size = size
        self.win_condition = win_condition
        self.board = [' '] * (size * size)
        self.current_player = 'X'
        self.game_over = False
        self.winning_combinations = self.generate_winning_combinations()

    def generate_winning_combinations(self):
        """Vygeneruje všechny možné výherní kombinace pro danou velikost hracího pole a podmínku na výhru."""
        combinations = []
        size = self.size
        win = self.win_condition

        # Horizontální kombinace
        for row in range(size):
            for col in range(size - win + 1):
                start = row * size + col
                combination = [start + i for i in range(win)]
                combinations.append(combination)

        # Vertikální kombinace
        for col in range(size):
            for row in range(size - win + 1):
                start = row * size + col
                combination = [start + i * size for i in range(win)]
                combinations.append(combination)

        # Diagonální kombinace (zleva doprava)
        for row in range(size - win + 1):
            for col in range(size - win + 1):
                start = row * size + col
                combination = [start + i * (size + 1) for i in range(win)]
                combinations.append(combination)

        # Diagonální kombinace (zprava doleva)
        for row in range(size - win + 1):
            for col in range(win - 1, size):
                start = row * size + col
                combination = [start + i * (size - 1) for i in range(win)]
                combinations.append(combination)

        return combinations

    def make_move(self, position):
        """Provede tah na zvolené pozici, pokud je volná a hra ještě neskončila."""
        if not self.game_over and self.board[position] == ' ':
            self.board[position] = self.current_player
            if self.check_winner():
                self.game_over = True  # Hra skončila
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
        return False

    def check_winner(self):
        """Zkontroluje, zda někdo vyhrál nebo zda je remíza."""
        for combo in self.winning_combinations:
            if all(self.board[i] == self.board[combo[0]] != ' ' for i in combo):
                return self.board[combo[0]]  # Vrátí vítěze ('X' nebo 'O')
        if ' ' not in self.board:
            self.game_over = True  # Remíza, hra skončila
            return 'Tie'
        return None

    def get_winning_combination(self):
        """Vrátí kombinaci, která vyhrála, nebo None."""
        for combo in self.winning_combinations:
            if all(self.board[i] == self.board[combo[0]] != ' ' for i in combo):
                return combo
        return None

    def reset_board(self):
        """Resetuje hrací desku."""
        self.board = [' '] * (self.size * self.size)
        self.current_player = 'X'
        self.game_over = False  # Obnoví stav hry
@views.route('/save_game', methods=['POST'])
def save_game():
    """Save the game state with a name and difficulty level."""
    game_name = request.form.get('game_name')
    difficulty = request.form.get('difficulty')

    if not game_name or not difficulty:
        return jsonify({'status': 'error', 'message': 'Game name and difficulty are required.'}), 400

    # Example of saving the game - replace with actual database logic
    saved_game = {
        'name': game_name,
        'difficulty': difficulty,
        'board': game.board,
        'current_player': game.current_player,
        'game_over': game.game_over
    }
    # For now, we just print it. Replace this with database save logic.
    print(f"Game saved: {saved_game}")

    return jsonify({'status': 'success', 'message': f'Game "{game_name}" saved successfully!'})
game = TicTacToe()
from .models import Game  # Import modelu
@views.route('/challenges', methods=['GET', 'POST'])
def challenges():
    """Display a list of games with filtering and sorting options."""
    
    # Get filter and sort parameters from the query string
    name_filter = request.args.get('name', '')
    difficulty_filter = request.args.get('difficulty', '')
    sort_by = request.args.get('sort_by', 'created_at')  # Default sorting by creation date
    sort_order = request.args.get('sort_order', 'asc')  # Default sorting order (ascending)
    
    # Construct the query
    query = Game.query
    
    if name_filter:
        query = query.filter(Game.name.ilike(f'%{name_filter}%'))
    
    if difficulty_filter:
        query = query.filter(Game.difficulty == difficulty_filter)
    
    if sort_order == 'desc':
        query = query.order_by(getattr(Game, sort_by).desc())
    else:
        query = query.order_by(getattr(Game, sort_by).asc())
    
    # Get the filtered and sorted games
    games = query.all()
    
    
    return render_template('challenges.html', games=games)


@views.route('/game/<uuid>', methods=['GET', 'PUT'])
def game_page(uuid):
    game = Game.query.filter_by(uuid=uuid).first()
    if not game:
        abort(404, description="Game not found.")
    
    ttt_game = TicTacToe(size=15, win_condition=5)
    flat_board = [cell if cell != '' else ' ' for row in game.board for cell in row]
    ttt_game.board = flat_board
    
    ttt_game.current_player = game.current_player
    ttt_game.game_over = game.game_state != 'In Progress'
    
    # Determine game state right away based on current board status
    game_state = ttt_game.get_game_state()

    if request.method == 'GET':
        # Render the game page with the current state
        return render_template('game_page.html', game=game, board=game.board, game_state=game_state)

    if request.method == 'PUT':
        data = request.get_json()
        print(f"Received data: {data}")  # Ladicí výpis
        row, col = data.get('row'), data.get('col')
        print(f"Row: {row}, Col: {col}")  # Ladicí výpis
        if row is None or col is None or not (0 <= row < 15 and 0 <= col < 15):
            abort(400, description="Invalid position.")
        
        position = row * 15 + col
        if not ttt_game.make_move(position):
            abort(400, description="Invalid move or position already taken.")
        
        # Update board and game state
        flat_board = ttt_game.board
        game.board = [flat_board[i:i + 15] for i in range(0, len(flat_board), 15)]
        game.current_player = ttt_game.current_player
        game.game_state = ttt_game.get_game_state()
        db.session.commit()

        # Save to database
        
        
        # Return the updated game state
        return jsonify({
            'status': 'success',
            'board': game.board,
            'currentPlayer': game.current_player,
            'gameState': game.game_state
        })
class TicTacToe:
    def __init__(self, size=15, win_condition=5):
        self.size = size
        self.win_condition = win_condition
        self.board = [' '] * (size * size)
        self.current_player = 'X'
        self.game_over = False
        self.winning_combinations = self.generate_winning_combinations()

    def generate_winning_combinations(self):
        """Generate all possible winning combinations."""
        # Horizontal, vertical, diagonal combinations
        combinations = []
        size = self.size
        win = self.win_condition
        # Horizontal combinations
        for row in range(size):
            for col in range(size - win + 1):
                start = row * size + col
                combination = [start + i for i in range(win)]
                combinations.append(combination)
        # Vertical combinations
        for col in range(size):
            for row in range(size - win + 1):
                start = row * size + col
                combination = [start + i * size for i in range(win)]
                combinations.append(combination)
        # Diagonal combinations (left to right)
        for row in range(size - win + 1):
            for col in range(size - win + 1):
                start = row * size + col
                combination = [start + i * (size + 1) for i in range(win)]
                combinations.append(combination)
        # Diagonal combinations (right to left)
        for row in range(size - win + 1):
            for col in range(win - 1, size):
                start = row * size + col
                combination = [start + i * (size - 1) for i in range(win)]
                combinations.append(combination)
        return combinations

    def get_game_state(self):
        """Determine the game state: Opening, Midgame, Endgame, or Invalid."""
        x_count = self.board.count('X')
        o_count = self.board.count('O')
        
        # Check valid move count
        if not (x_count == o_count or x_count == o_count + 1):
            return "Invalid"
        
        # Check if there is a winner or potential win
        winner = self.check_winner()
        if winner:
            return "Endgame"
        
        # Check if there are enough moves to be considered midgame
        if x_count + o_count <= 5:
            return "Opening"
        
        return "Midgame"
        
    
    def make_move(self, position):
        print(f"Attempting move at position: {position} by player {self.current_player}")
    
    # Kontrola, zda je pozice volná v 1D seznamu
        if self.board[position] != ' ':
            print(f"Position {position} is already taken by {self.board[position]}")  # Ladicí výpis
            return False

    # Provádění tahu
        self.board[position] = self.current_player
    
    # Zkontrolujte, zda je vítěz
        if self.check_winner():
            self.game_over = True
            print(f"Player {self.current_player} wins!")
        else:
        # Přepnutí hráče
            self.current_player = 'O' if self.current_player == 'X' else 'X'
    
        return True

    def check_winner(self):
    
        for combo in self.winning_combinations:
            print(f"Checking combination: {combo}")  # Ladicí výpis pro zjištění, která kombinace je kontrolována
        # Check if all positions in the combination are occupied by the same player (either 'X' or 'O')
            if all(self.board[i] == self.board[combo[0]] != ' ' for i in combo):
                print(f"Winner found: {self.board[combo[0]]}")  # Ladicí výpis pro zjištění vítěze
                return self.board[combo[0]]  # Return the winner ('X' or 'O')

    # If there are no more empty spaces and no winner, it's a tie
        if ' ' not in self.board:
            self.game_over = True  # It's a tie
            print("It's a tie.")  # Ladicí výpis pro remízu
            
        
        print("No winner yet.")  # Ladicí výpis pro zjištění, že zatím není vítěz
        return None  # No winner yet   

    def reset_board(self):
        """Reset the game board."""
        self.board = [' '] * (self.size * self.size)
        self.current_player = 'X'
        self.game_over = False








  

