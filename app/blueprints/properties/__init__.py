from flask import Blueprint

properties_bp = Blueprint('properties', __name__)

# Import des vues pour enregistrer les routes
from . import views
