from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail
import os
from dotenv import load_dotenv
load_dotenv()  # loads variables from .env into os.environ
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
mail = Mail()

def create_app(): 
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:AMwyeRlQEsnViGvcDPiUITbFeuAXaAlv@turntable.proxy.rlwy.net:47657/railway'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('website', 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.secret_key = os.getenv("SECRET_KEY")

    app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv("BREVO_SMTP_USER")
    app.config['MAIL_PASSWORD'] = os.getenv("BREVO_SMTP_KEY")
    app.config['MAIL_DEFAULT_SENDER'] = ('No Reply - ReVibe', 'revibe.app.mail@gmail.com')  # Verified sender
    app.config['MAIL_DEBUG'] = True


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
