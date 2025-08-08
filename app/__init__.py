from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Where to redirect for login
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.payment import bp as payment_bp
    app.register_blueprint(payment_bp, url_prefix='/payment')

    from app.videos import bp as videos_bp
    app.register_blueprint(videos_bp, url_prefix='/videos')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Import models and define user_loader to avoid circular imports
    from app.models import User, Subscription, Video
    import uuid

    @login_manager.user_loader
    def load_user(user_id):
        """Load user from the database."""
        try:
            # Flask-Login sends the user_id as a string
            return User.query.get(uuid.UUID(user_id))
        except (ValueError, TypeError):
            return None

    # Define a shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Video': Video,
            'Subscription': Subscription
        }

    return app
