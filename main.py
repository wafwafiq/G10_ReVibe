print("Starting application...")

try:
    from website import create_app
    print("Imported create_app")
    
    from website import db, socketio
    print("Imported db and socketio")
    
    from website.models import User
    print("Imported User model")

    app = create_app()
    print("App created successfully")

    if __name__ == "__main__":
        print("Running main...")
        with app.app_context():
            print("In app context")
            db.create_all()
            print("Tables created")
            db.reflect()
            print("DB reflected")
            if not User.query.first():
                print("Creating test user...")
                test_user = User(
                    user_id=1,
                    name="Alice",
                    password="password123",
                    email="alice@example.com"
                )
                db.session.add(test_user)
                db.session.commit()
                print("Test user created")
            else:
                print("Users already exist")

        print("Starting server...")
        socketio.run(app, debug=True, host='127.0.0.1', port=5000)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()