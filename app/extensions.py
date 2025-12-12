from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Configuration du login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = "Veuillez vous connecter pour accéder à ImmoGest."
login_manager.login_message_category = "warning"


