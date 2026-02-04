from flask import Flask
from datetime import datetime
from models import db
from flask_mailjet import Mailjet
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import Config


# Initialize extensions (no app binding yet)
mailjet = Mailjet()
csrf = CSRFProtect()
migrate = Migrate()


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    mailjet.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Register Jinja template filter
    @app.template_filter("iso_to_dmy_hm")
    def iso_to_dmy_hm(value):
        if not value:
            return ""
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime("%d-%m-%Y %H:%M")
        except ValueError:
            return value

    # Context processor to inject user into all templates
    @app.context_processor
    def inject_user():
        from flask import session
        from utils.helpers import get_current_user

        user = get_current_user() if "userid" in session else None
        return {"user": user}

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.rooms import rooms_bp
    from routes.bookings import bookings_bp
    from routes.support import support_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(admin_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
