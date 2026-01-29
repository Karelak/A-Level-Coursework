from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User
from forms import LoginForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
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

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
