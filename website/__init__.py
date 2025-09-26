from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail
import os
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
    app.secret_key = SECRET_KEY= your_flask_secret

    app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = '97f16d001@smtp-brevo.com'  # Brevo login
    app.config['MAIL_PASSWORD'] = 'xsmtpsib-42e8d8053bbebf7e3c3ca45b004d0c7f9f3c9f20e63440c8f0df56fc4e067738-Sjc8QyVnfdJUC149'             # the SMTP key (you pasted above)
    app.config['MAIL_DEFAULT_SENDER'] = ('No Reply - ReVibe', 'revibe.app.mail@gmail.com')
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
