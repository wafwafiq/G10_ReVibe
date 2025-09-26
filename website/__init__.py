from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env into environment
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()

def create_app(): 
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:AMwyeRlQEsnViGvcDPiUITbFeuAXaAlv@turntable.proxy.rlwy.net:47657/railway'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('website', 'static', 'uploads')
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
    socketio.init_app(app)

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


    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response



    return app
