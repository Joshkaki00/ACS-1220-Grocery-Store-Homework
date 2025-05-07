from flask import Flask
from grocery_app.extensions import db, bcrypt, login_manager

__all__ = ['db', 'bcrypt', 'login_manager']

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev'

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from grocery_app.routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    # Create database tables
    with app.app_context():
        # Create a test store if none exists
        from grocery_app.models import GroceryStore
        if not GroceryStore.query.first():
            test_store = GroceryStore(
                title='Test Store',
                address='123 Test St'
            )
            db.session.add(test_store)
            db.session.commit()

    return app 