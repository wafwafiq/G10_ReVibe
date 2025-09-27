from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()  # Load variables from .env into environment

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)

    # Database config (Railway MySQL in this case)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+pymysql://root:AMwyeRlQEsnViGvcDPiUITbFeuAXaAlv'
        '@turntable.proxy.rlwy.net:47657/railway'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # File upload handling
    if os.path.exists('/app'):  # Railway environment
        app.config['UPLOAD_FOLDER'] = '/app/uploads'
    else:  # Local development
        app.config['UPLOAD_FOLDER'] = os.path.join('website', 'static', 'uploads')

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

    # ----------------------------
    # ✅ Brevo API configuration
    # ----------------------------
    brevo_key = os.getenv("BREVO_API_KEY")
    if not brevo_key:
        raise RuntimeError("❌ BREVO_API_KEY not set in .env")

    # Store the Brevo client on the Flask app object
    app.brevo_client = sib_api_v3_sdk.ApiClient(configuration)
    app.brevo_api = sib_api_v3_sdk.TransactionalEmailsApi(app.brevo_client)

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')

    return app


def create_admin():  # defined admin account
    from .models import User
    admin_email = "admin@revibe.com"
    admin_password = "admin123"
    admin_name = "Administrator"

    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin = User(
            name=admin_name,
            email=admin_email,
            password=admin_password,
            confirmed=True,    # skip email verification
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()