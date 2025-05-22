from config import Config
from app.utils.db import db
from app.utils.extensions import login_manager, bcrypt
from app.routes.auth import auth_bp
from app.routes.patron import patron_bp
from app.models import Patron
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patron_bp)

    return app
