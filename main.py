from flask import Flask
from website.models import db, User   # import db + User model

app = Flask(__name__)

# MySQL connection (replace password with yours)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ogezuJ4qNR7Jk9Mb@localhost/revibe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"  # needed for sessions

# Initialize database
db.init_app(app)

@app.route('/')
def index():
    # Example: fetch users from DB
    users = User.query.all()
    return '<br>'.join([f"{u.user_id} - {u.name} ({u.email})" for u in users])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables if not present
    app.run(debug=True)