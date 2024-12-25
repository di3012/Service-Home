# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config
from flask_migrate import Migrate
# from app.models import db

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'login'  # Redirect to login page if not authenticated

    with app.app_context():
       from . import routes  # Import routes here, once the app is created
      #  db.create_all() 

    return app
