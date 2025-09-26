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
    app.config['MAIL_USERNAME'] = "97ee25002@smtp-brevo.com"
    app.config['MAIL_PASSWORD'] = "xsmtpsib-abc60c9036f2a6cb67056e2bf7e919d77eceda81ea7a295d6e82483ba814c44e-YgaLzBQ6qjhs5RcV"
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
