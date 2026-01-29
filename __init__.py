from flask import Flask
from models import db
from datetime import datetime
from flask_mailjet import Mailjet
from flask_wtf.csrf import CSRFProtect

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.rooms import rooms_bp
from routes.bookings import bookings_bp
from routes.support import support_bp
from routes.admin import admin_bp
from config import Config
from flask_migrate import Migrate

app = Flask(__name__)
mailjet = Mailjet()
migrate = Migrate(app, db)
csrf = CSRFProtect()


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


def create_app():
    app.config.from_object(Config)
    db.init_app(app)
    mailjet.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
