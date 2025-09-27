from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail
import os
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env into environment
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
mail = Mail()

def create_app(): 
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:AMwyeRlQEsnViGvcDPiUITbFeuAXaAlv@turntable.proxy.rlwy.net:47657/railway'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('website', 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.secret_key = "your_secret_key"

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = (
        os.getenv('MAIL_SENDER_NAME'),
        os.getenv('MAIL_SENDER_EMAIL')
    )
    app.config['MAIL_DEBUG'] = os.getenv('MAIL_DEBUG', 'False') == 'True'


    db.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)  
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')


    return app
def create_admin():#defined admin account
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