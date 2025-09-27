from website import create_app, create_admin
from website import db, socketio
from website.models import User

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        import eventlet
        import eventlet.wsgi
        db.create_all()
        create_admin()
        db.reflect()
        if not User.query.first():
            test_user = User(
                user_id=1,
                name="Alice",
                password="password123",
                email="alice@example.com"
            )
            db.session.add(test_user)
            db.session.commit()
    
    socketio.run(app, host="0.0.0.0", port=5000)