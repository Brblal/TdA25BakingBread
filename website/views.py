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

game = TicTacToe()
from .models import Game  # Import modelu
@views.route('/challenges', methods=['GET', 'POST'])
def challenges():
    
    
    games = Game.query.all()  # Načtení všech záznamů z tabulky `games`
    return render_template('challenges.html', games=games)
@views.route('/game/<uuid>', methods=['GET'])
def game_page(uuid):
    """Render a page for a specific game by UUID."""
    game = Game.query.filter_by(uuid=uuid).first()
    if not game:
        abort(404, description="Game not found.")
    return render_template('game_page.html', game=game)
    







  

