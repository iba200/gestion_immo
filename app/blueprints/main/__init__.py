from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

from . import views
