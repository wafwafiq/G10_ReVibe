from flask import Blueprint, render_template , request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from .models import User, Item, Conversation, Message
from flask_socketio import join_room, leave_room, send
from . import db, socketio
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
#start chat between seller and buyer
@views.route('/start_chat/<int:item_id>/<int:seller_id>')
@login_required
def start_chat(item_id, seller_id):
    seller = User.query.get_or_404(seller_id) #looks for seller and item
    item = Item.query.get_or_404(item_id)

    conversation = Conversation.query.filter( #checks whether seller and buyer have an existing conversation
    ((Conversation.user1_id == current_user.user_id) & (Conversation.user2_id == seller.user_id)) |
    ((Conversation.user1_id == seller.user_id) & (Conversation.user2_id == current_user.user_id))
    ).filter_by(item_id=item.item_id).first()


    if not conversation: #create conversation if it doesnt exist
        conversation = Conversation(
        item_id=item.item_id,
        user1_id=current_user.user_id,
        user2_id=seller.user_id
    )
    db.session.add(conversation)
    db.session.commit()
    #redirects to chatroom with seller
    return redirect(url_for('views.chatroom', conversation_id=conversation.conversation_id))

@views.route('/chatlog',methods=['GET','POST']) #shows all chats of current buyer with sellers
@login_required
def chats():

    chats = Conversation.query.filter(
        (Conversation.user1_id == current_user.user_id) | 
        (Conversation.user2_id == current_user.user_id)).all() #searches and shows all existing chats
    
    return render_template('chatlog.html', chats=chats) 

@views.route("/chat/<int:conversation_id>") #chatroom between seller and buyer
@login_required
def chatroom(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id) #shows which conversation you are in
    messages = Message.query.filter_by(conversation_id=conversation.conversation_id).order_by(Message.created_at).all() #shows all messages in the conversation
    item = Item.query.get_or_404(conversation.item_id)
    return render_template('chatroom.html', conversation=conversation, messages=messages, item=item)

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

@socketio.on('join') #decorator to tell the server a buyer has entered a conversation
def handle_join(data):
    room = data['conversation_id']
    join_room(room)

@socketio.on('send_message') #decorator to send messages to user
def handle_message(data):
    room = data['conversation_id']
    msg_content = data['content']

    message = Message(conversation_id=room,
                    sender_id=current_user.user_id,
                    content=msg_content
    )
    db.session.add(message)
    db.session.commit()

    send({'user': current_user.name, 'content': msg_content}, to=room)