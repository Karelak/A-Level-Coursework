from flask import Blueprint, render_template, redirect, url_for, session, flash
from ..models import db, User, SupportTicket
from ..utils.helpers import is_logged_in, get_current_user
from ..forms import SupportTicketForm, ReplyTicketForm
from ..utils.mailjet import send_support_ticket_email, send_ticket_update_email
from datetime import datetime
import json

support_bp = Blueprint("support", __name__)


@support_bp.route("/support", methods=["GET", "POST"])
def support():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    form = SupportTicketForm()

    if form.validate_on_submit():
        admin = User.query.filter_by(role="admin").first()
        if admin:
            ticket = SupportTicket(
                userid=user.userid,
                adminid=admin.userid,
                subject=form.subject.data,
                message=form.message.data,
            )
            db.session.add(ticket)
            db.session.commit()

            try:
                send_support_ticket_email(
                    user.email, ticket.ticketid, ticket.subject, ticket.message
                )
            except Exception as e:
                print(f"Error sending support ticket email: {str(e)}")

            flash("Support ticket submitted successfully", "success")
            return redirect(url_for("support.support"))
        else:
            flash("No admin available. Please try again later.", "error")

    tickets = SupportTicket.query.filter_by(userid=user.userid).all()
    return render_template("support/form.html", user=user, form=form, tickets=tickets)


@support_bp.route("/support/<int:ticket_id>/reply", methods=["POST"])
def reply_ticket(ticket_id):
    if not is_logged_in() or session.get("role") != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))

    user = get_current_user()
    ticket = SupportTicket.query.get_or_404(ticket_id)

    if user.role != "admin":
        flash("You cannot reply to tickets", "error")
        return redirect(url_for("dashboard.dashboard"))

    form = ReplyTicketForm()

    if form.validate_on_submit():
        reply_text = form.reply.data.strip()

        # Parse existing replies from JSON
        try:
            replies = json.loads(ticket.replies) if ticket.replies else []
        except json.JSONDecodeError:
            replies = []

        # Add new reply
        reply_obj = {
            "author": f"{user.fname} {user.lname}",
            "role": "admin",
            "message": reply_text,
            "timestamp": datetime.now().isoformat(),
        }
        replies.append(reply_obj)

        # Update ticket
        ticket.replies = json.dumps(replies)
        ticket.status = "replied"
        db.session.commit()

        # Build conversation chain for email
        conversation = [
            {
                "author": ticket.user.fname + " " + ticket.user.lname,
                "role": "user",
                "message": ticket.message,
                "timestamp": ticket.created_at,
            }
        ] + replies

        try:
            send_ticket_update_email(
                ticket.user.email, ticket.ticketid, ticket.subject, conversation
            )
        except Exception as e:
            print(f"Error sending ticket update email: {str(e)}")

        flash("Reply sent successfully and email notification sent to user", "success")

    return redirect(url_for("dashboard.admin_dashboard"))


@support_bp.route("/support/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    if not is_logged_in() or session.get("role") != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))
    user = get_current_user()
    ticket = SupportTicket.query.get_or_404(ticket_id)
    if user.role != "admin":
        flash("You cannot delete tickets", "error")
        return redirect(url_for("dashboard.dashboard"))

    db.session.delete(ticket)
    db.session.commit()

    flash("Ticket deleted successfully", "success")
    return redirect(url_for("dashboard.admin_dashboard"))

    flash("Ticket deleted successfully", "success")
    return redirect(url_for("dashboard.admin_dashboard"))
