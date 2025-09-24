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
        return str(self.user_id)
    
class Item(db.Model):
    __tablename__ = 'items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100))
    item_condition = db.Column(db.Enum('new', 'used', 'refurbished'), nullable=False)
    location = db.Column(db.String(150))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    seller = db.relationship('User', backref='items')

    def __repr__(self):
        return f"<Item {self.title}>"
    
    def get_id(self):
        return str(self.item_id)
    
class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    conversation_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")

    def participants(self):
        return [self.user1, self.user2]
    
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])

class Message(db.Model):
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.conversation_id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    
    sender = db.relationship('User', foreign_keys=[sender_id])