from flask import Blueprint, render_template, redirect, url_for, session, flash
from models import db, User, Booking, Room, SupportTicket
from routes.rooms import sorter

dashboard_bp = Blueprint("dashboard", __name__)


def is_logged_in():
    return "userid" in session


def get_current_user():
    if is_logged_in():
        return db.session.get(User, session["userid"])
    return None


@dashboard_bp.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


@dashboard_bp.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    bookings = Booking.query.filter_by(userid=user.userid).all()
    bookings_sorted = sorter(
        bookings,
        key_func=lambda booking: (
            booking.room.roomname if booking.room is not None else "",
            booking.timebegin,
        ),
    )

    return render_template("dashboard/main.html", user=user, bookings=bookings_sorted)


@dashboard_bp.route("/admin/dashboard")
def admin_dashboard():
    if not is_logged_in() or session.get("role") != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))

    user = get_current_user()
    all_bookings = Booking.query.all()
    all_users = User.query.all()
    all_rooms = Room.query.all()
    tickets = SupportTicket.query.all()

    bookings_sorted = sorter(
        all_bookings,
        key_func=lambda booking: (
            booking.room.roomname if booking.room is not None else "",
            booking.timebegin,
        ),
    )

    users_sorted = sorter(
        all_users,
        key_func=lambda user: (user.fname, user.lname),
    )

    rooms_sorted = sorter(
        all_rooms,
        key_func=lambda room: (room.floor, room.roomname),
    )

    tickets_sorted = sorter(
        tickets,
        key_func=lambda ticket: ticket.created_at,
    )

    return render_template(
        "dashboard/admin.html",
        user=user,
        bookings=bookings_sorted,
        users=users_sorted,
        rooms=rooms_sorted,
        tickets=tickets_sorted,
    )
