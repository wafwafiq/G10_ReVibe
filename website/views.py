from flask import Blueprint, render_template
from .models import User

views = Blueprint('views', __name__)

@views.route('/home')
def home():
    return render_template('main.html')

@views.route('/posts')
def posts():
    return ('posts page')

@views.route('/catalog')
def catalog():
    return ('catalog page')

@views.route('/map')
def map():
    return ('map page')

@views.route('/chat')
def chats():
    return ('chat page')

@views.route('/users')
def lists_users():
    # Example: fetch users from DB
    users = User.query.all()
    return '<br>'.join([f"{u.user_id} - {u.name} ({u.email})" for u in users])  