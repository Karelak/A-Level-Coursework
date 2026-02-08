import pyotp
from datetime import datetime, timedelta


def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6)
    return totp.now()


def get_otp_expiry(minutes=5):
    return datetime.now() + timedelta(minutes=minutes)
