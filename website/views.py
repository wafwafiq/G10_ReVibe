from flask import Blueprint, render_template , request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from .models import User, Item
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
    if request.method == 'POST': 
        image = request.files['item_images']
        title = request.form['item_title']
        description = request.form['item_description']
        price = request.form['item_price']
        category = request.form['item_category']
        condition = request.form['item_condition']
        location = request.form['item_location']

        _, ext = os.path.splitext(image.filename) 
        filename = str(uuid.uuid4()) + ext 
        image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) 

        new_item = Item(
            title = title,
            description = description,
            price = float(price),
            category = category,
            item_condition = condition,
            location = location,
            seller_id = current_user.user_id,
            image_filename=filename
        )
        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('views.catalog'))


    return render_template('post_creation.html')
 
@views.route('/edit/<int:item_id>', methods=['GET','POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == "POST":
        item.image = request.files['item_images'] 
        item.title = request.form['item_title']
        item.description = request.form['item_description']
        item.price = request.form['item_price']
        item.category = request.form['item_category']
        item.item_condition = request.form['item_condition']
        item.location = request.form['item_location']
        db.session.commit()
        return redirect(url_for('views.home'))
    
    return render_template("edit_item.html", item=item)

@views.route('/catalog', methods=['GET'])
@login_required
def catalog():



    search_query = request.args.get("search", "").lower()
    category_filter = request.args.get("category_filter", "")

    query = Item.query

    if search_query:
        query = query.filter(Item.title.ilike(f"%{search_query}%"))

    if category_filter:
        query = query.filter_by(category=category_filter)

    filtered_items = query.all()

    categories = ["books", "electronics", "furniture", "clothing", "sports", "kitchen"]

    
    return render_template(
        "catalog.html",
        items=filtered_items,
        categories=categories,
        search_query=search_query,
        selected_category=category_filter
    ) 

@views.route('/start_chat/<int:seller_id>')
@login_required
def start_chat(seller_id):
    seller = User.query.get_or_404(seller_id)


    chat = (Chat.query
            .filter(Chat.participants.any(id=current_user.id))
            .filter(Chat.participants.any(id=seller.id)).first())


    if not chat:
        chat = Chat()
        chat.participants.append(current_user)
        chat.participants.append(seller)
        db.session.add(chat)
        db.session.commit()

    return redirect(url_for('views.chatroom', chat_id=chat.id))

@views.route('/chatlog',methods=['GET','POST'])
@login_required
def chats():
    chats = Chat.query.filter(Chat.participants.any(id=current_user.id)).all()
    return render_template('chatlog.html', chats=chats) 

views.route("/chat/<int:chat_id>")
@login_required
def chatroom(chat_id):

    return render_template('chatroom.html', chat=chat, messages=messages)

@views.route('/')
def index():
    users = User.query.all()
    return '<br>'.join([f"{u.user_id} - {u.name} ({u.email})" for u in users])

@views.route('/item/<int:item_id>')
@login_required
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == "POST":
        if "name" in request.form and "email" in request.form:
            
            current_user.name = request.form["name"]
            current_user.email = request.form["email"]
            db.session.commit()
            flash("Profile updated successfully!")

        elif "current_password" in request.form:
            current_pass = request.form["current_password"]
            new_pass = request.form["new_password"]
            confirm_pass = request.form["confirm_password"]

            if current_user.password == current_pass:  
                if new_pass == confirm_pass:
                    current_user.password = new_pass   
                    db.session.commit()
                    flash("Password updated successfully!")
                else:
                    flash("Passwords do not match.")
            else:
                flash("Current password is incorrect.")

        return redirect('/settings')

    return render_template("settings.html", user=current_user)
