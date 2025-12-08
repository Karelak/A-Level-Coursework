from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User

auth_bp = Blueprint("auth", __name__)


def is_logged_in():
    return "userid" in session


def get_current_user():
    if is_logged_in():
        return db.session.get(User, session["userid"])
    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session["userid"] = user.userid
            session["role"] = user.role
            flash("Login successful", "success")
            if user.role == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))
            else:
                # non-admin role
                return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid email or password", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
