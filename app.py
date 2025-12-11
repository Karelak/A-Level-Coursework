from flask import Flask
from utils.models import db, User
import os
from datetime import datetime


# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.rooms import rooms_bp
from routes.bookings import bookings_bp
from routes.support import support_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///meeting_rooms.db"
app.config["SECRET_KEY"] = os.urandom(32)


db.init_app(app)


# filters
@app.template_filter("iso_to_dmy_hm")
def iso_to_dmy_hm(value):
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d-%m-%Y %H:%M")
    except ValueError:
        return value


# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(support_bp)
app.register_blueprint(admin_bp)


def init_db():
    with app.app_context():
        db.create_all()
        # Create admin account if no users exist
        if User.query.count() == 0:
            admin_user = User(
                fname="Admin",
                lname="User",
                email="admin@caa.co.uk",
                password="admin123",
                role="admin",
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Database initialised with starter admin account")


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)
