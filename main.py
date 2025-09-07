from website import create_app
from website import db
from website.models  import User

app = create_app()



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.reflect()
        if not User.query.first():
            test_user = User(
                user_id=1,  # must be an integer, not "U001"
                name="Alice",
                password="password123",
                email="alice@example.com"
            )
            db.session.add(test_user)
            db.session.commit()

    app.run(debug=True)