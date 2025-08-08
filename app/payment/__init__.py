from flask import Blueprint

bp = Blueprint('payment', __name__, template_folder='templates')

from app.payment import routes
