from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.models import db, Room, Booking
from utils.helpers import is_logged_in, get_current_user, sorter

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/rooms")
def rooms():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    all_rooms = Room.query.all()
    sorted_rooms = sorter(all_rooms, key_func=lambda room: (room.floor, room.roomname))
    return render_template("rooms/list.html", user=user, rooms=sorted_rooms)


@rooms_bp.route("/rooms/<int:room_id>")
def room_detail(room_id):
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    room = Room.query.get_or_404(room_id)
    bookings = Booking.query.filter_by(roomid=room_id).all()

    return render_template("rooms/detail.html", user=user, room=room, bookings=bookings)


@rooms_bp.route("/admin/rooms/new", methods=["POST"])
def admin_create_room():
    if not is_logged_in() or session.get("role") != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))

    roomname = request.form.get("roomname", "").strip()
    floor = request.form.get("floor", "").strip()

    # check if all fields are provided
    if not all([roomname, floor]):
        flash("All fields are required", "error")
        return redirect(url_for("dashboard.admin_dashboard"))

    # validate room name length
    if len(roomname) < 1:
        flash("Room name cannot be empty", "error")
        return redirect(url_for("dashboard.admin_dashboard"))

    # validate floor is a valid integer
    try:
        floor_num = int(floor)
    except ValueError:
        flash("Floor must be a valid number", "error")
        return redirect(url_for("dashboard.admin_dashboard"))

    # validate floor is non-negative
    if floor_num < 0:
        flash("Floor must be 0 or greater", "error")
        return redirect(url_for("dashboard.admin_dashboard"))
    # check for duplicate room on same floor
    existing_room = Room.query.filter_by(floor=floor_num, roomname=roomname).first()
    if existing_room:
        flash("A room with this name already exists on this floor", "error")
        return redirect(url_for("dashboard.admin_dashboard"))

    try:
        room = Room(roomname=roomname, floor=floor_num)
        db.session.add(room)
        db.session.commit()
        flash("Room created successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating room: {str(e)}", "error")

    return redirect(url_for("dashboard.admin_dashboard"))


@rooms_bp.route("/admin/rooms/<int:room_id>/delete", methods=["POST"])
def delete_room(room_id):
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    if not user or user.role != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))

    room = db.session.get(Room, room_id)
    if not room:
        flash("Room not found", "error")
        return redirect(url_for("dashboard.admin_dashboard"))

    # check for existing bookings before deletion
    existing_booking = Booking.query.filter_by(roomid=room_id).first()
    if existing_booking:
        flash("Cannot delete room with existing bookings", "error")
        return redirect(url_for("dashboard.admin_dashboard"))

    try:
        db.session.delete(room)
        db.session.commit()
        flash("Room deleted successfully", "success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while deleting the room", "error")

    return redirect(url_for("dashboard.admin_dashboard"))
