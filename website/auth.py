from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db


auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        fullName = request.form.get('fullName')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')

    
        new_user = User(email=email,name=username ,password=password)
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        return redirect(url_for('views.home'))

    return render_template('login.html')

@auth.route('/logout')
def logout():
    return('logged out')