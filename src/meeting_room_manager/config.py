import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
    MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
    MAILJET_DEFAULT_SENDER = os.getenv("MAILJET_DEFAULT_SENDER")
    SQLALCHEMY_DATABASE_URI = "sqlite:///meeting_rooms.db"
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class Postgres_Config(Config):
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = os.getenv("PG_PORT", 5432)
    PG_USER = os.getenv("PG_USER", "user")
    PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
    PG_DB = os.getenv("PG_DB", "mydb")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )
