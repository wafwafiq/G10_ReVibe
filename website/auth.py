from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
import random
import os

# Brevo SDK
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

auth = Blueprint('auth', __name__)

# --- Setup Brevo API ---
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
brevo_client = sib_api_v3_sdk.ApiClient(configuration)
email_api = sib_api_v3_sdk.TransactionalEmailsApi(brevo_client)


# --- Token Helpers ---
def generate_token(email, salt, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.secret_key)
    return s.dumps(email, salt=salt)

def verify_token(token, salt, max_age=3600):
    s = URLSafeTimedSerializer(current_app.secret_key)
    try:
        return s.loads(token, salt=salt, max_age=max_age)
    except Exception:
        return None


# --- Brevo Email Sender ---
def send_email(subject, recipients, body, html=None):
    sender = {"email": "revibeapp@gmail.com", "name": "Revibe"}
    to = [{"email": r} for r in recipients]

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        text_content=body,
        html_content=html or body
    )

    try:
        response = email_api.send_transac_email(email)
        print("Email sent! Message ID:", response['messageId'])
        return True
    except ApiException as e:
        print("Error sending email:", e)
        return False


# --- Signup ---
@auth.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')  
        password = request.form.get('password')
        confirmPassword = request.form.get('confirm_password')

        if not email or not name or not password or not confirmPassword:
            flash("Please fill in all required fields", category="error")
            return redirect(url_for('auth.sign_up'))

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
            password=password,   # ⚠️ store hashed in production
            created_at=datetime.utcnow()
        )

        db.session.add(new_user)
        db.session.commit()

        token = generate_token(new_user.email, salt="email-confirm")
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = f"<p>Welcome {new_user.name},</p><p>Click <a href='{confirm_url}'>here</a> to confirm your account.</p>"

        if send_email("Confirm Your Email", [new_user.email], body="Please confirm your email", html=html):
            flash("Account created successfully! Please check your email.", category="success")
        else:
            flash("Account created, but email service is not available.", category="warning")

        return redirect(url_for('auth.login'))

    return render_template('signup.html')


# --- Login ---
@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('views.admin_main' if current_user.is_admin else 'views.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Please provide both email and password", category="error")
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            if not user.confirmed and not user.is_admin:
                flash("Please confirm your email before logging in.", category="warning")
                return redirect(url_for('auth.login'))

            login_user(user, remember=True)
            flash(f"Welcome {user.name}!", category="success")
            return redirect(url_for('views.admin_main' if user.is_admin else 'views.home'))
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


# --- Confirm Email ---
@auth.route('/confirm/<token>')
def confirm_email(token):
    email = verify_token(token, salt="email-confirm")
    if not email:
        flash("The confirmation link is invalid or has expired.", category="error")
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", category="error")
        return redirect(url_for('auth.login'))

    user.confirmed = True
    db.session.commit()

    flash("Your account has been confirmed! You can now log in.", category="success")
    return redirect(url_for('auth.login'))


# --- Request reset ---
@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()

            html = f"<p>Hello {user.name},</p><p>Your OTP code is <b>{otp}</b>. It expires in 10 minutes.</p>"
            send_email("Reset Your Password (OTP)", [user.email], body=f"Your OTP is {otp}", html=html)

            flash("OTP has been sent to your email. Enter it below.", "info")
            return redirect(url_for('auth.verify_otp', email=email))
        else:
            flash("No account found with that email.", "error")
    return render_template('reset_request.html')


# --- Verify OTP ---
@auth.route('/reset_password/verify/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Invalid email.", "error")
        return redirect(url_for('auth.reset_request'))

    if request.method == 'POST':
        otp = request.form.get('otp')

        if user.otp_code != otp or not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:
            flash("Invalid or expired OTP.", "error")
            return redirect(url_for('auth.verify_otp', email=email))

        return redirect(url_for('auth.reset_password_form', email=email))

    return render_template('verify_otp.html', email=email)


# --- Reset Password Form ---
@auth.route('/reset_password/form/<email>', methods=['GET', 'POST'])
def reset_password_form(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('auth.reset_request'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash("Passwords do not match!", "error")
            return redirect(url_for('auth.reset_password_form', email=email))

        user.password = password  # ⚠️ hash in production
        user.otp_code = None
        user.otp_expires_at = None
        db.session.commit()

        flash("Password has been reset. You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('reset_password_form.html', email=email)
