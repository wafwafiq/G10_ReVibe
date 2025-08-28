from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(): 
    app = Flask(__name__)
    # MySQL code from main moved to init
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ogezuJ4qNR7Jk9Mb@localhost/revibe'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "your_secret_key"

    db.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)  # removed int(), matches VARCHAR primary key
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')


    return app
