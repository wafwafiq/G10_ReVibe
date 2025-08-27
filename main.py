from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# MySQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ogezuJ4qNR7Jk9Mb@localhost/revibe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"

# Initialize database
db = SQLAlchemy(app)

# Define User model matching your MySQL table
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(50), primary_key=True)  # VARCHAR(50) primary key
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

# Route to display users
@app.route('/')
def index():
    users = User.query.all()
    return '<br>'.join([f"{u.user_id} - {u.name} ({u.email})" for u in users])

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables if not present

        # Example: add a test user if table is empty
        if not User.query.first():
            test_user = User(
                user_id="U001",
                name="Alice",
                password="password123",
                email="alice@example.com"
            )
            db.session.add(test_user)
            db.session.commit()

    app.run(debug=True)
