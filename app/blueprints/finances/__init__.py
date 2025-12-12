from flask import Blueprint

finances_bp = Blueprint('finances', __name__)

from . import views
