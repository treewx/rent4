import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = None

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('NEXTAUTH_SECRET', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432/rent4')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CSRF Configuration for production
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow HTTPS behind proxy

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    global limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.properties import properties_bp
    from routes.payments import payments_bp
    from routes.akahu import akahu_bp
    from routes.stripe_routes import stripe_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(akahu_bp)
    app.register_blueprint(stripe_bp)

    # Import models to register them with SQLAlchemy
    from models import user, property

    # Create tables (only if database is available)
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Database tables will be created automatically when deployed")

    # Initialize scheduler
    from services.scheduler import init_scheduler
    init_scheduler(app)

    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')