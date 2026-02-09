from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import User, db
from ..forms import LoginForm, VerifyOTPForm
from ..utils.otp import generate_otp, get_otp_expiry
from ..utils.mailjet import send_otp_email
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Check if any users exist - redirect to setup if not
    user_count = User.query.count()
    if user_count == 0:
        return redirect(url_for("admin.setup"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        password_ok = False
        if user:
            if check_password_hash(user.password, password):
                password_ok = True
            elif user.password == password:
                user.password = generate_password_hash(password)
                db.session.commit()
                password_ok = True

        if password_ok:
            # Generate OTP and send email
            otp_code = generate_otp()
            otp_expiry = get_otp_expiry(minutes=5)

            try:
                send_otp_email(email, otp_code, expiration_minutes=5)

                # Store OTP in session temporarily
                session["pending_otp"] = otp_code
                session["pending_otp_expiry"] = otp_expiry.isoformat()
                session["pending_userid"] = user.userid
                session["pending_email"] = email

                flash(
                    "OTP code sent to your email. Please check and enter it below.",
                    "info",
                )
                return redirect(url_for("auth.verify_2fa"))
            except Exception as e:
                flash(f"Error sending OTP: {str(e)}", "error")
        else:
            flash("Invalid email or password", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    # Check if user has initiated login
    if "pending_userid" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    # Check if OTP has expired
    otp_expiry = session.get("pending_otp_expiry")
    if otp_expiry and datetime.fromisoformat(otp_expiry) < datetime.now():
        session.pop("pending_otp", None)
        session.pop("pending_otp_expiry", None)
        session.pop("pending_userid", None)
        session.pop("pending_email", None)
        flash("OTP expired. Please login again.", "error")
        return redirect(url_for("auth.login"))

    form = VerifyOTPForm()

    if form.validate_on_submit():
        entered_otp = form.otp.data
        stored_otp = session.get("pending_otp")

        if entered_otp == stored_otp:
            # OTP is correct - complete login
            userid = session.pop("pending_userid")
            session.pop("pending_otp", None)
            session.pop("pending_otp_expiry", None)
            session.pop("pending_email", None)

            user = db.session.get(User, userid)

            session.permanent = True
            session["userid"] = user.userid
            session["role"] = user.role
            flash("Login successful!", "success")

            if user.role == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))
            else:
                return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid OTP code. Please try again.", "error")

    pending_email = session.get("pending_email", "your email")
    return render_template("auth/2fa.html", form=form, email=pending_email)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
