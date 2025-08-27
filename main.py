from website import create_app,db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables if not present
    app.run(debug=True)