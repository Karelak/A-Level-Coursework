import pyotp
from datetime import datetime, timedelta


def generate_otp():
    """Generate a random OTP code using pyotp"""
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6)
    return totp.now()


def get_otp_expiry(minutes=5):
    """Get OTP expiry time"""
    return datetime.now() + timedelta(minutes=minutes)
