from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .models import User  # you need this for queries in index()

views = Blueprint('views', __name__)

@views.route('/home')
@login_required
def home():
    return render_template('main.html')

@views.route('/posts')
def posts():
    return render_template('post_creation.html') 

@views.route('/catalog')
def catalog():
    return render_template('catalog.html') 

@views.route('/map')
def map():
    return 'map page'

@views.route('/chat')
def chats():
    return render_template('chatlog.html') 

@views.route('/')
def index():
    users = User.query.all()
    return '<br>'.join([f"{u.user_id} - {u.name} ({u.email})" for u in users])

@views.route('/item/<int:item_id>')
def item_detail(item_id):
    return render_template('item_detail.html')  

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == "POST":
        if "name" in request.form and "email" in request.form:
            # Update profile info
            current_user.name = request.form["name"]
            current_user.email = request.form["email"]
            db.session.commit()
            flash("Profile updated successfully!")

        elif "current_password" in request.form:
            current_pass = request.form["current_password"]
            new_pass = request.form["new_password"]
            confirm_pass = request.form["confirm_password"]

            if current_user.password == current_pass:  # direct string compare
                if new_pass == confirm_pass:
                    current_user.password = new_pass   # store plain password
                    db.session.commit()
                    flash("Password updated successfully!")
                else:
                    flash("Passwords do not match.")
            else:
                flash("Current password is incorrect.")

        return redirect('/settings')

    return render_template("settings.html", user=current_user)