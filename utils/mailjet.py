import os
from flask import current_app
from flask_mailjet.loader import render_email_template


def send_otp_email(recipient_email, otp_code, expiration_minutes=5):
    try:
        sender_email = os.environ.get("MAILJET_DEFAULT_SENDER")
    except KeyError:
        print("MAILJET_DEFAULT_SENDER not set in environment variables.")
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


def send_support_ticket_email(recipient_email, ticket_id, subject, description):
    try:
        sender_email = os.environ.get("MAILJET_DEFAULT_SENDER")
    except KeyError:
        print("MAILJET_DEFAULT_SENDER not set in environment variables.")

    email_html = render_email_template(
        "support_ticket.html",
        ticket_id=ticket_id,
        subject=subject,
        description=description,
    )
    try:
        mailjet = current_app.extensions.get("mailjet")
        if not mailjet:
            raise Exception("Mailjet extension not initialized.")
        mailjet.send_email(
            sender={"Email": sender_email},
            recipients=recipient_email,
            subject=f"Support Ticket #{ticket_id}",
            html=email_html,
        )
    except Exception as e:
        raise Exception(f"Failed to send support ticket email: {str(e)}")


def send_booking_confirmation_email(
    recipient_email, booking_id, room_name, time_begin, time_finish
):
    try:
        sender_email = os.environ.get("MAILJET_DEFAULT_SENDER")
    except KeyError:
        print("MAILJET_DEFAULT_SENDER not set in environment variables.")

    email_html = render_email_template(
        "booking_confirmation.html",
        booking_id=booking_id,
        room_name=room_name,
        time_begin=time_begin,
        time_finish=time_finish,
    )
    try:
        mailjet = current_app.extensions.get("mailjet")
        if not mailjet:
            raise Exception("Mailjet extension not initialized.")
        mailjet.send_email(
            sender={"Email": sender_email},
            recipients=recipient_email,
            subject=f"Booking Confirmation #{booking_id}",
            html=email_html,
        )
    except Exception as e:
        raise Exception(f"Failed to send booking confirmation email: {str(e)}")


def send_ticket_update_email(recipient_email, ticket_id, subject, conversation_chain):
    try:
        sender_email = os.environ.get("MAILJET_DEFAULT_SENDER")
    except KeyError:
        print("MAILJET_DEFAULT_SENDER not set in environment variables.")

    email_html = render_email_template(
        "support_ticket_update.html",
        ticket_id=ticket_id,
        subject=subject,
        conversation_chain=conversation_chain,
    )
    try:
        mailjet = current_app.extensions.get("mailjet")
        if not mailjet:
            raise Exception("Mailjet extension not initialized.")
        mailjet.send_email(
            sender={"Email": sender_email},
            recipients=recipient_email,
            subject=f"Support Ticket #{ticket_id} - New Reply",
            html=email_html,
        )
    except Exception as e:
        raise Exception(f"Failed to send ticket update email: {str(e)}")
