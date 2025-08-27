from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'   

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.name}>"