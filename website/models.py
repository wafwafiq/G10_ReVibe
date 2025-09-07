from . import db
from datetime import datetime
from flask_login import UserMixin 

class User(db.Model, UserMixin):
    __tablename__ = 'users'   

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.name}>"
    
    def get_id(self):
        return str(self.user_id) #fixed code stopping from logging