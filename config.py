import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
    MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
    MAILJET_DEFAULT_SENDER = os.getenv("MAILJET_DEFAULT_SENDER")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///meeting_rooms.db"
    )
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
