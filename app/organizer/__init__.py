from flask import Blueprint

organizer_bp = Blueprint('organizer', __name__, url_prefix='/organizer')

from app.organizer import routes
