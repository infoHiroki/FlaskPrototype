from flask import Blueprint

bp = Blueprint('videos', __name__, template_folder='templates')

from app.videos import routes
