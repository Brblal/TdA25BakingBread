from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from datetime import datetime, timedelta
from flask_login import LoginManager


# Inicializace db
db = SQLAlchemy()
DB_NAME = "database.db"
def round_to_nearest_minute(dt):
    if dt is not None:
        return dt.replace(second=0, microsecond=0) + timedelta(minutes=(dt.second >= 30))
    return None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['UPLOAD_FOLDER'] = 'static/files'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.jinja_env.filters['round_to_nearest_minute'] = round_to_nearest_minute
    db.init_app(app)

    # Registrovat blueprints
    from .views import views
    from .routes import api_bp  # Import API blueprint

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api/v1')  # Register API blueprint

    # Importovat modely až po inicializaci db
    from .models import Game  
    login_manager = LoginManager()
    login_manager.login_view = 'views.login'  # Název view funkce pro login
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))# Importujte model hry

    # Vytvořit databázi, pokud neexistuje
    with app.app_context():
        create_database()

    return app

def create_database():
    # Pokud databáze neexistuje, vytvoř ji
    if not path.exists(DB_NAME):
        db.create_all()
        print('Created Database!')


def add_game(game_data):
    """Funkce pro přidání nové hry"""
    from .models import Game  # Import modelu hry do funkce
    game = Game(
        name=game_data["name"],
        difficulty=game_data["difficulty"],
        board=game_data["board"]
    )
    db.session.add(game)
    db.session.commit()
    print(f"Game '{game.name}' added to database!")

