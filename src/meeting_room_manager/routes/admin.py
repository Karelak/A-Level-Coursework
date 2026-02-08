from flask import Blueprint, redirect, url_for, session, flash, render_template
from ..models import db, User, Room
from ..utils.helpers import is_logged_in, get_current_user
from ..forms import SetupForm, AdminCreateUserForm, AdminCreateRoomForm

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/setup", methods=["GET", "POST"])
def setup():
    # Check if any users exist
    user_count = User.query.count()
    if user_count > 0:
        return redirect(url_for("auth.login"))

    form = SetupForm()

    if form.validate_on_submit():
        fname = form.fname.data.strip()
        lname = form.lname.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        # Validate name lengths
        if len(fname) < 2 or len(lname) < 2:
            flash("First and last names must be at least 2 characters long", "error")
            return redirect(url_for("admin.setup"))

        # Validate password length
        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return redirect(url_for("admin.setup"))

        try:
            user = User(
                fname=fname, lname=lname, email=email, password=password, role="admin"
            )
            db.session.add(user)
            db.session.commit()
            flash("Admin account created successfully. You can now login.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating admin account: {str(e)}", "error")

    return render_template("admin/setup.html", form=form)


@admin_bp.route("/admin/users/new", methods=["POST"])
def admin_create_user():
    if not is_logged_in() or session.get("role") != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))

    form = AdminCreateUserForm()

    if form.validate_on_submit():
        fname = form.fname.data.strip()
        lname = form.lname.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data
        role = form.role.data

        # Validate name lengths
        if len(fname) < 2 or len(lname) < 2:
            flash("First and last names must be at least 2 characters long", "error")
            return redirect(url_for("dashboard.admin_dashboard"))

        # Validate password length
        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return redirect(url_for("dashboard.admin_dashboard"))

        # Check for existing email
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already exists", "error")
            return redirect(url_for("dashboard.admin_dashboard"))

        try:
            user = User(
                fname=fname, lname=lname, email=email, password=password, role=role
            )
            db.session.add(user)
            db.session.commit()
            flash("User created successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating user: {str(e)}", "error")

    return redirect(url_for("dashboard.admin_dashboard"))


@admin_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    if not user or user.role != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))

    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        flash("User not found", "error")
        return redirect(url_for("dashboard.admin_dashboard"))

    # check for existing bookings for user before deletion
    if user_to_delete.bookings:
        flash("Cannot delete user with existing bookings", "error")
        return redirect(url_for("dashboard.admin_dashboard"))
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "error")
    return redirect(url_for("dashboard.admin_dashboard"))


@admin_bp.route("/admin/rooms/new", methods=["POST"])
def admin_create_room():
    if not is_logged_in() or session.get("role") != "admin":
        flash("Access denied", "error")
        return redirect(url_for("dashboard.dashboard"))

    form = AdminCreateRoomForm()

    if form.validate_on_submit():
        roomname = form.roomname.data.strip()
        floor = form.floor.data.strip()

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
        existing_room = (
            db.session.query(db.Model.__table__)
            .get("rooms")
            .filter(
                db.and_(
                    db.Model.__table__.get("rooms").c.floor == floor_num,
                    db.Model.__table__.get("rooms").c.roomname == roomname,
                )
            )
            .first()
        )

        # Simpler check using query
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
