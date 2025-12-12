from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager

def create_app(config_name='default'):
    app = Flask(__name__)

    # Chargement de la config
    app.config.from_object(config[config_name])

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models

    # Enregistrement des Blueprints (Modules)

    # Nous utilisons des imports locaux pour éviter les cycles
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.properties import properties_bp
    app.register_blueprint(properties_bp, url_prefix='/properties')

    from app.blueprints.finances import finances_bp
    app.register_blueprint(finances_bp, url_prefix='/finances')

    return app
