from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db
from datetime import datetime
import uuid  # for generating unique user_id since it's VARCHAR

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        fullName = request.form.get('fullName')  # optional if you have another field
        password = request.form.get('password')
        confirmPassword = request.form.get('confirm_password')

        # Basic validation
        if password != confirmPassword:
            flash("Passwords do not match!", category="error")
            return redirect(url_for('auth.sign_up'))

        # Check if email or username already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.name == username)
        ).first()
        if existing_user:
            flash("Email or username already exists!", category="error")
            return redirect(url_for('auth.sign_up'))

        # Generate unique user_id (since your MySQL table uses VARCHAR)
        user_id = str(uuid.uuid4())[:8]  # short unique id

        new_user = User(
            user_id=user_id,
            name=username,
            email=email,
            password=password,
            created_at=datetime.utcnow()
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", category="success")
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check credentials
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            flash(f"Welcome {user.name}!", category="success")
            return redirect(url_for('views.home'))
        else:
            flash("Invalid email or password", category="error")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    flash("Logged out successfully", category="success")
    return redirect(url_for('views.home'))
