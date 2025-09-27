from flask import Blueprint, render_template , request, redirect, url_for, current_app, flash, send_from_directory
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
    if item.seller_id != current_user.user_id:
        flash("You can only edit your own posts", "error")
        return redirect(url_for('views.home'))
    
    if request.method == "POST":
        
        item.title = request.form.get('item_title')
        item.description = request.form.get('item_description')
        item.price = float(request.form.get('item_price'))
        item.category = request.form.get('item_category')
        item.item_condition = request.form.get('item_condition')
        item.location = request.form.get('item_location')
        
        if 'item_images' in request.files:
            image = request.files['item_images']
            if image and image.filename:
                _, ext = os.path.splitext(image.filename) 
                filename = str(uuid.uuid4()) + ext 
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                item.image_filename=filename

        db.session.commit()
        flash("Item updated successfully", "success")
        return redirect(url_for('views.home'))
    
    return render_template("edit_item.html", item=item)

@views.route('/toggle_sold/<int:item_id>', methods=['POST'])
@login_required
def toggle_sold_status(item_id):
    item = Item.query.get_or_404(item_id)
    if item.seller_id != current_user.user_id:
        flash("You can only modify your own posts.", "error")
        return redirect(url_for('views.home'))
    
    item.is_sold = not item.is_sold
    db.session.commit()
    
    status = "marked as sold" if item.is_sold else "relisted"
    flash(f"Item has been {status} successfully!", "success")
    return redirect(url_for('views.edit_item', item_id=item_id))

@views.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.seller_id != current_user.user_id:
        flash("You can only delete your own posts.", "error")
        return redirect(url_for('views.home'))
    
    try:

        conversations = Conversation.query.filter_by(item_id=item_id).all()
        for conversation in conversations:
            Message.query.filter_by(conversation_id=conversation.conversation_id).delete()
            db.session.delete(conversation)
        
        item_title = item.title
        db.session.delete(item)
        db.session.commit()
        flash(f'Item "{item_title}" deleted successfully!', "success")
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting item: {str(e)}', "error")
    
    return redirect(url_for('views.home'))


@views.route('/catalog', methods=['GET'])
@login_required
def catalog():



    search_query = request.args.get("search", "").lower()
    category_filter = request.args.get("category_filter", "")

    query = Item.query.filter_by(is_sold=False)

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

@views.route('/start_chat/<int:item_id>/<int:seller_id>')
@login_required
def start_chat(item_id, seller_id):
    seller = User.query.get_or_404(seller_id)
    item = Item.query.get_or_404(item_id)

    if item.seller_id == current_user.user_id:
        flash("You cannot chat with yourself about your own item", "error")
        return redirect(url_for('views.item_detail', item_id=item_id))

    conversation = Conversation.query.filter(
    ((Conversation.user1_id == current_user.user_id) & (Conversation.user2_id == seller.user_id)) |
    ((Conversation.user1_id == seller.user_id) & (Conversation.user2_id == current_user.user_id))
    ).filter_by(item_id=item.item_id).first()


    if not conversation:
        conversation = Conversation(
        item_id=item.item_id,
        user1_id=current_user.user_id,
        user2_id=seller.user_id
    )
    db.session.add(conversation)
    db.session.commit()
    
    return redirect(url_for('views.chatroom', conversation_id=conversation.conversation_id))

@views.route('/chatlog',methods=['GET','POST']) 
@login_required
def chats():

    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.user_id) | 
        (Conversation.user2_id == current_user.user_id)
    ).options(
        db.joinedload(Conversation.item),
        db.joinedload(Conversation.user1),
        db.joinedload(Conversation.user2),
        db.joinedload(Conversation.messages)
    ).all()

    processed_conversations =[]
    for conversation in conversations:
        conversation.other_user = conversation.get_other_user(current_user.user_id)
        conversation.last_message = conversation.get_last_message()
        processed_conversations.append(conversation)
    
    return render_template('chatlog.html', conversations=processed_conversations) 

@views.route("/chat/<int:conversation_id>")
@login_required
def chatroom(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    messages = Message.query.filter_by(conversation_id=conversation.conversation_id).order_by(Message.created_at).all() 
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


@views.route('/admin')
@login_required
def admin_main():
    if not current_user.is_admin:
        flash("Access denied", "error")
        return redirect(url_for('auth.login'))
    return render_template('main_admin.html')

@views.route('/admin/users')
@login_required
def admin_users():
    users = User.query.order_by(User.name).all()
    return render_template('admin_users.html', users=users)

@views.route('/admin/posts')
@login_required
def admin_posts():
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('admin_posts.html', posts=items)

@views.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        
        for item in user.items:
            conversations = Conversation.query.filter_by(item_id=item.item_id).all()
            for conversation in conversations:
                Message.query.filter_by(conversation_id=conversation.conversation_id).delete()
                db.session.delete(conversation)
            db.session.delete(item)
        
        conversations = Conversation.query.filter(
            (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
        ).all()
        for conversation in conversations:
            Message.query.filter_by(conversation_id=conversation.conversation_id).delete()
            db.session.delete(conversation)
        
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.name}" deleted successfully!', "success")
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', "error")
    
    return redirect(url_for('views.admin_users'))

@views.route('/admin/delete_post/<int:item_id>', methods=['POST'])
@login_required
def admin_delete_post(item_id):
    item = Item.query.get_or_404(item_id)
    try:
        
        conversations = Conversation.query.filter_by(item_id=item_id).all()
        for conversation in conversations:
            Message.query.filter_by(conversation_id=conversation.conversation_id).delete()
            db.session.delete(conversation)
        
        item_title = item.title
        db.session.delete(item)
        db.session.commit()
        flash(f'Post "{item_title}" deleted successfully!', "success")
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting post: {str(e)}', "error")
    
    return redirect(url_for('views.admin_posts'))

@socketio.on('join')
def handle_join(data):
    try:
        room = str(data['conversation_id'])
        join_room(room)
        print(f"User {current_user.user_id} joined room {room}")
    except Exception as e:
        print(f"Error in handle_join: {e}")

@socketio.on('send_message')
def handle_message(data):
    try:
        room = str(data['conversation_id'])
        msg_content = data['content']
        
        if not msg_content or len(msg_content.strip()) == 0:
            return
        
        if len(msg_content) > 500:
            msg_content = msg_content[500]

        message = Message(
            conversation_id=data['conversation_id'],
            sender_id=current_user.user_id,
            content=msg_content.strip()
        )
        db.session.add(message)
        db.session.commit()
        socketio.emit("receive_message", {
        "sender_id": current_user.user_id,
        "content": msg_content.strip(),
        "created_at": message.created_at.isoformat(),
        "sender_name": current_user.name
        } ,room=room)

        socketio.emit('message_sent',{
            'message_id': message.message_id,
            'created_at': message.created_at.isoformat()
        }, room=room)
    except Exception as e:
        print(f"Error in handle_message: {e}")
        socketio.emit('error', {'message': 'Failed to send message'}, room=request.sid)