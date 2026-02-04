import os
from flask import current_app
from flask_mailjet.loader import render_email_template


def send_otp_email(recipient_email, otp_code, expiration_minutes=5):
    sender_email = os.environ.get("MAILJET_DEFAULT_SENDER", "noreply@example.com")
    email_html = render_email_template(
        "2fa.html", otp_code=otp_code, expiration_minutes=expiration_minutes
    )
    try:
        mailjet = current_app.extensions.get("mailjet")
        if not mailjet:
            raise Exception("Mailjet extension not initialized.")
        mailjet.send_email(
            sender={"Email": sender_email},
            recipients=recipient_email,
            subject="Your Two-Factor Authentication Code",
            html=email_html,
        )
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
