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

from flask import session
import uuid
from uuid import uuid4
from flask_login import LoginManager
from flask_login import login_user

from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user


from flask import abort
from .models import User  # Pokud je User model definován v models.py
from .models import Entry
from .models import Gamefp
from sqlalchemy.orm.attributes import flag_modified



views = Blueprint('views', __name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['UPLOAD_FOLDER'] = 'static/files'

api = Blueprint('api', __name__)



# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "views.login"  # Ujistěte se, že tento odkaz odpovídá vaší přihlašovací stránce

# Set up the login view, so users are redirected to the login page when not authenticated



@views.route('/', methods=['GET', 'POST'])
def home():
    
    
  
    return render_template("home.html")
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))
@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Pouze email pro přihlášení
        password = request.form.get('password')

        # Hledání uživatele podle emailu
        user = User.query.filter_by(email=email).first()
        print(f"eee{email}")
        if user:
            print(f"User ID: {user.get_id()}")  # Tohle ukáže ID uživatele
            if check_password_hash(user.password, password):
                flash('Přihlášen úspěšně!', category="success")
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Špatné heslo!', category="error")
        else:
            flash('Email neexistuje!', category="error")


    return render_template('login.html', user=current_user)



@views.route('/create-acc', methods=['GET', 'POST'])
def create_acc():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        user_name = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        # Kontrola, jestli už uživatel s tímto emailem nebo jménem existuje
        user = User.query.filter_by(email=email).first()
        user2 = User.query.filter_by(user_name=user_name).first()
        
        if user:
            flash('Email již existuje', category='error')
        elif user2:
            flash('Uživatelské jméno již existuje', category='error')
        elif len(email) < 4:
            flash('Email musí mít více než 3 znaky', category='error')
        elif len(name) < 2:
            flash('Jméno musí mít více než 1 znak', category='error')
        elif password1 != password2:
            flash('Hesla se neshodují', category='error')
        elif len(password1) < 6:
            flash('Heslo musí mít více než 6 znaků', category='error')
        else:
            # Vytvoření nového uživatele bez 'admin' hodnoty
            new_user = User(email=email, name=name, user_name=user_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Účet byl úspěšně vytvořen', category='success')
            return redirect(url_for('views.login'))  # Přesměrování na přihlašovací stránku po vytvoření účtu
    return render_template('createAcc.html', user=current_user)  # Vrátí formulář, pokud není POST požadavek
@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html", current_user=current_user)




      
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
@views.route('/freeplay', methods=['POST'])
def freeplay_page():
    new_game = Gamefp()
    new_game.uuid = str(uuid.uuid4())
    new_game.player_x_uuid = new_game.uuid  # The first player gets the game UUID as their player UUID
    new_game.player_o_uuid = ""  # The second player is not assigned yet

    db.session.add(new_game)
    db.session.commit()

    return redirect(url_for('views.fp_game_page', game_uuid=new_game.uuid, player_uuid=new_game.player_x_uuid))  # Redirect

@views.route('/freeplay/confirm_join/<game_uuid>', methods=['GET'])
def confirm_join(game_uuid):
    # Pokud chcete vynutit generování nového UUID, ignorujte query parametr
    player_uuid = str(uuid.uuid4())
    return render_template("confirm_join.html", game_uuid=game_uuid, player_uuid=player_uuid)


@views.route('/freeplay/join/<game_uuid>', methods=['POST'])
def join_game_post(game_uuid):
    # Získáme player_uuid z formuláře
    player_uuid = request.form.get("player_uuid")
    
    game = Gamefp.query.filter_by(uuid=game_uuid).first()
    if not game:
        abort(404, description="Game not found.")

    if game.player_o_uuid:  # Pokud je hráč O již přiřazen, hra je plná
        return "The game is full!", 400

    # Pokud z formuláře neobdržíme player_uuid, vygenerujeme nové (ale ideálně se tam vždy předá)
    if not player_uuid:
        player_uuid = str(uuid.uuid4())
    
    print("Before join:", game.player_x_uuid, game.player_o_uuid)
    game.player_o_uuid = player_uuid  # Přiřadíme UUID pro hráče O
    print("After join:", game.player_x_uuid, game.player_o_uuid)
    
    db.session.commit()  # Uložíme změny

    return redirect(url_for('views.fp_game_page', game_uuid=game.uuid, player_uuid=player_uuid))


@views.route('/freeplay/game/<game_uuid>', methods=['GET'])
def fp_game_page(game_uuid):
    player_uuid = request.args.get("player_uuid")
    game = Gamefp.query.filter_by(uuid=game_uuid).first()
    if not game:
        abort(404, description="Game not found.")

    # Access players using player_x_uuid and player_o_uuid
    game_players = {
        'X': game.player_x_uuid,
        'O': game.player_o_uuid
    }

    # Determine the current player based on player_uuid
    if player_uuid == game.player_x_uuid:
        current_player = 'X'
    elif player_uuid == game.player_o_uuid:
        current_player = 'O'
    else:
        current_player = None

    

    return render_template("freeplay.html", game=game, game_players=game_players, player_uuid=player_uuid, current_player=current_player)
@views.route('/freeplay/game_state/<game_uuid>', methods=['GET'])
def get_game_state(game_uuid):
    game = Gamefp.query.filter_by(uuid=game_uuid).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404

    return jsonify({
        'board': game.board,
        'current_player': game.current_player,
        'game_state': game.game_state,
        
    })
@views.route('/freeplay/move/<game_uuid>', methods=['PUT'])
def make_move_fp(game_uuid):
    player_uuid = request.json.get('player_uuid')
    row = request.json.get('row')
    col = request.json.get('col')

    game = Gamefp.query.filter_by(uuid=game_uuid).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404

    # Check if player_uuid is valid
    if player_uuid != game.player_x_uuid and player_uuid != game.player_o_uuid:
        return jsonify({'error': 'Player not part of the game'}), 400

    # Determine whose turn it is
    if game.current_player == 'X' and player_uuid != game.player_x_uuid:
        return jsonify({'error': 'It\'s not your turn'}), 400
    elif game.current_player == 'O' and player_uuid != game.player_o_uuid:
        return jsonify({'error': 'It\'s not your turn'}), 400

    # Validate move (check if the cell is empty)
    if game.board[row][col] != '':
        return jsonify({'error': 'Cell already taken'}), 400

    # Make the move and update the board
    symbol = 'X' if player_uuid == game.player_x_uuid else 'O'
    game.board[row][col] = symbol

    # Flaguj, že atribut board byl změněn
    flag_modified(game, "board")

    # Switch player turn
    game.current_player = 'O' if game.current_player == 'X' else 'X'

    db.session.commit()

    return jsonify({
        'status': 'success',
        'board': game.board,
        'current_player': game.current_player,
        'game_state': game.game_state,
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
        combinations = []
        size = self.size
        win = self.win_condition
        # Horizontal, vertical, diagonal combinations
        for row in range(size):
            for col in range(size - win + 1):
                start = row * size + col
                combination = [start + i for i in range(win)]
                combinations.append(combination)
        for col in range(size):
            for row in range(size - win + 1):
                start = row * size + col
                combination = [start + i * size for i in range(win)]
                combinations.append(combination)
        for row in range(size - win + 1):
            for col in range(size - win + 1):
                start = row * size + col
                combination = [start + i * (size + 1) for i in range(win)]
                combinations.append(combination)
        for row in range(size - win + 1):
            for col in range(win - 1, size):
                start = row * size + col
                combination = [start + i * (size - 1) for i in range(win)]
                combinations.append(combination)
        return combinations

    def get_game_state(self):
        x_count = self.board.count('X')
        o_count = self.board.count('O')
        
        if not (x_count == o_count or x_count == o_count + 1):
            return "Invalid"
        
        winner = self.check_winner()
        if winner:
            return "Endgame"
        
        if x_count + o_count <= 5:
            return "Opening"
        
        return "Midgame"
    
    def make_move(self, position):
        if self.board[position] != ' ':
            return False  # Pokud je pozice už obsazena, vrátí False

        if self.current_player != 'X' and self.current_player != 'O':
            return False  # Pokud není správný hráč, vrátí False

        self.board[position] = self.current_player

        # Zkontrolujeme, zda je vítěz
        if self.check_winner():
            self.game_over = True
        else:
                # Přepneme na druhého hráče
            self.current_player = 'O' if self.current_player == 'X' else 'X'

        return True
        
    def check_winner(self):
        for combo in self.winning_combinations:
            if all(self.board[i] == self.board[combo[0]] != ' ' for i in combo):
                return self.board[combo[0]]
        if ' ' not in self.board:
            self.game_over = True
        return None

    def reset_board(self):
        self.board = [' '] * (self.size * self.size)
        self.current_player = 'X'
        self.game_over = False
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
class GamePage:
    def __init__(self, size=15, win_condition=5):
        self.size = size
        self.win_condition = win_condition
        self.board = [' '] * (self.size * self.size)
        self.current_player = 'X'  # První hráč je 'X'
        self.game_over = False
        self.winning_combinations = self.generate_winning_combinations()

    def generate_winning_combinations(self):
        """Generování všech možných vítězných kombinací."""
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

        # Diagonální kombinace (levá-prawe)
        for row in range(size - win + 1):
            for col in range(size - win + 1):
                start = row * size + col
                combination = [start + i * (size + 1) for i in range(win)]
                combinations.append(combination)

        # Diagonální kombinace (pravá-levá)
        for row in range(size - win + 1):
            for col in range(win - 1, size):
                start = row * size + col
                combination = [start + i * (size - 1) for i in range(win)]
                combinations.append(combination)

        return combinations

    def make_move(self, position):
        """Provést tah, pokud je pozice volná a hra není ukončena."""
        if self.game_over:
            return False
        
        if self.board[position] != ' ':
            return False

        # Provést tah
        self.board[position] = self.current_player

        # Zkontrolovat vítěze
        if self.check_winner():
            self.game_over = True
        else:
            # Přepnout na druhého hráče
            self.current_player = 'O' if self.current_player == 'X' else 'X'

        return True

    def check_winner(self):
        """Zkontroluje, zda je někdo vítěz."""
        for combo in self.winning_combinations:
            if all(self.board[i] == self.board[combo[0]] != ' ' for i in combo):
                return self.board[combo[0]]  # Vítěz 'X' nebo 'O'
        
        if ' ' not in self.board:  # Je remíza
            self.game_over = True
            return 'Tie'

        return None  # Žádný vítěz

    def reset_board(self):
        """Resetování herní desky pro novou hru."""
        self.board = [' '] * (self.size * self.size)
        self.current_player = 'X'
        self.game_over = False

    def get_board(self):
        """Vrátí aktuální stav herní desky."""
        return [self.board[i:i + self.size] for i in range(0, len(self.board), self.size)]








  

