from flask import Blueprint, render_template , request, redirect, url_for, current_app
from flask_login import login_required, current_user
from .models import User, Item #import item db
from . import db
import os 
import uuid

views = Blueprint('views', __name__)

@views.route('/home')
@login_required
def home():
    return render_template('main.html')

@views.route('/posts', methods=['GET','POST'])
@login_required
def posts():
    if request.method == 'POST': #added code for item input
        image = request.files['item_images']
        title = request.form['item_title']
        description = request.form['item_description']
        price = request.form['item_price']
        category = request.form['item_category']
        condition = request.form['item_condition']
        location = request.form['item_location']

        _, ext = os.path.splitext(image.filename) #keeps file extension
        filename = str(uuid.uuid4()) + ext #creates unique file name
        image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) #code to save images to uploads folder

        new_item = Item(
            title = title,
            description = description,
            price = float(price),
            category = category,
            item_condition = condition,
            location = location,
            seller_id = current_user.user_id 
        ) #item data creation
        db.session.add(new_item)
        db.session.commit() #saved item data to database

        return redirect(url_for('views.catalog'))


    return render_template('post_creation.html') 

@views.route('/catalog', methods=['GET','POST'])
@login_required
def catalog():
    items = Item.query.all()
    return render_template('catalog.html', items=items) 

@views.route('/map')
@login_required
def map():
    return 'map page'

@views.route('/chat')
@login_required
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
