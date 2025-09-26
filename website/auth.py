from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db, mail
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from datetime import datetime
import smtplib

auth = Blueprint('auth', __name__)


def generate_token(email, salt, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.secret_key)
    return s.dumps(email, salt=salt)

def verify_token(token, salt, max_age=3600):
    s = URLSafeTimedSerializer(current_app.secret_key)
    try:
        return s.loads(token, salt=salt, max_age=max_age)
    except Exception:
        return None

def send_email(subject, recipients, body, html=None):
    msg = Message(subject, recipients=recipients, body=body, html=html)
    try:
        mail.send(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication failed.")
        return False
    except Exception as e:
        print(f"Email error: {e}")
        return False

# --- Signup ---
@auth.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')  
        password = request.form.get('password')
        confirmPassword = request.form.get('confirm_password')

        if password != confirmPassword:
            flash("Passwords do not match!", category="error")
            return redirect(url_for('auth.sign_up'))

        existing_user = User.query.filter(
            (User.email == email) | (User.name == name)
        ).first()
        if existing_user:
            flash("Email or username already exists!", category="error")
            return redirect(url_for('auth.sign_up'))

        new_user = User(
            name=name,
            email=email,
            password=password,   # ⚠️ plain text, hash later
            created_at=datetime.utcnow()
        )

        db.session.add(new_user)
        db.session.commit()


        return redirect(url_for('auth.login'))

    return render_template('signup.html')

# --- Login ---
@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email, password=password).first()
        if user:

            flash(f"Welcome {user.name}!", category="success")
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash("Invalid email or password", category="error")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# --- Logout ---
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", category="success")
    return redirect(url_for('auth.login'))

# --- Request reset ---
@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_token(user.email, salt="password-reset")
            reset_url = url_for('auth.reset_token', token=token, _external=True)
            html = f"<p>Hello {user.name},</p><p>Click <a href='{reset_url}'>here</a> to reset your password.</p>"
            send_email("Reset Your Password", [user.email], body="Click the link to reset your password", html=html)
            flash("Password reset email sent! Check your inbox.", "info")
            return redirect(url_for('auth.login'))
        else:
            flash("No account found with that email.", "error")
    return render_template('reset_request.html')

# --- Reset form ---
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    email = verify_token(token, salt="password-reset")
    if not email:
        flash("The reset link is invalid or expired.", "error")
        return redirect(url_for('auth.reset_request'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('auth.reset_request'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash("Passwords do not match!", "error")
            return redirect(url_for('auth.reset_token', token=token))

        user.password = password   # stored raw
        db.session.commit()
        flash("Password has been reset. You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
