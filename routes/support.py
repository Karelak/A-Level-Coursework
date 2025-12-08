from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Admin, SupportTicket

support_bp = Blueprint("support", __name__)


def is_logged_in():
    return "userid" in session


def get_current_user():
    if is_logged_in():
        return db.session.get(User, session["userid"])
    return None


@support_bp.route("/support", methods=["GET", "POST"])
def support():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()

    if request.method == "POST":
        subject = request.form.get("subject")
        message = request.form.get("message")

        admin = Admin.query.first()
        if admin:
            ticket = SupportTicket(
                userid=user.userid,
                adminid=admin.adminid,
                subject=subject,
                message=message,
            )
            db.session.add(ticket)
            db.session.commit()
            flash("Support ticket submitted successfully", "success")
            return redirect(url_for("support.support"))
        else:
            flash("No admin available. Please try again later.", "error")

    tickets = SupportTicket.query.filter_by(userid=user.userid).all()
    return render_template("support/form.html", user=user, tickets=tickets)


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
