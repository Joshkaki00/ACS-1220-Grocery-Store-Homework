from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object('grocery_app.config.Config')

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from grocery_app.routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    return app


@login_manager.user_loader
def load_user(user_id):
    from grocery_app.models import User
    return User.query.get(int(user_id))