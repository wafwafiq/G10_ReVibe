from flask import Blueprint, render_template , request #adam z added request
from .models import User

views = Blueprint('views', __name__)

@views.route('/home')
def home():
    return render_template('main.html')

@views.route('/posts')
def posts():
    return render_template('post_creation.html') #changed by adam z

@views.route('/catalog')
def catalog():
    return render_template('catalog.html') #changed by adam z

@views.route('/map')
def map():
    return ('map page')

@views.route('/chat')
def chats():
    return ('chat page')


@views.route('/')
def index():
    users = User.query.all()
    return '<br>'.join([f"{u.user_id} - {u.name} ({u.email})" for u in users])

@views.route('/item/<int:item_id>')
def item_detail(item_id):
    return render_template('item_detail.html')  
