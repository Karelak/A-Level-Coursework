from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    DateTimeLocalField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, ValidationError
from datetime import datetime


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address"),
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Password is required")]
    )


class VerifyOTPForm(FlaskForm):
    otp = StringField(
        "OTP Code",
        validators=[DataRequired(message="OTP code is required")],
    )


class SetupForm(FlaskForm):
    fname = StringField(
        "First Name",
        validators=[DataRequired(message="First name is required")],
    )
    lname = StringField(
        "Last Name",
        validators=[DataRequired(message="Last name is required")],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address"),
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Password is required")]
    )


class BookingForm(FlaskForm):
    roomid = SelectField(
        "Room", validators=[DataRequired(message="Please select a room")], coerce=int
    )
    timebegin = DateTimeLocalField(
        "Start Time",
        validators=[DataRequired(message="Start time is required")],
        format="%Y-%m-%dT%H:%M",
    )
    timefinish = DateTimeLocalField(
        "End Time",
        validators=[DataRequired(message="End time is required")],
        format="%Y-%m-%dT%H:%M",
    )

    def validate_timefinish(self, field):
        if self.timebegin.data and field.data:
            if field.data <= self.timebegin.data:
                raise ValidationError("End time must be after start time")

    def validate_timebegin(self, field):
        if field.data and field.data < datetime.now():
            raise ValidationError("Cannot create bookings in the past")

    def validate_duration(self):
        if self.timebegin.data and self.timefinish.data:
            duration = self.timefinish.data - self.timebegin.data
            duration_seconds = duration.total_seconds()
            if duration_seconds > 8 * 3600:
                raise ValidationError("Booking duration cannot exceed 8 hours")
            if duration_seconds < 30 * 60:
                raise ValidationError("Booking duration must be at least 30 minutes")


class SupportTicketForm(FlaskForm):
    subject = StringField(
        "Subject", validators=[DataRequired(message="Subject is required")]
    )
    message = TextAreaField(
        "Message", validators=[DataRequired(message="Message is required")]
    )


class AdminCreateUserForm(FlaskForm):
    fname = StringField(
        "First Name",
        validators=[DataRequired(message="First name is required")],
    )
    lname = StringField(
        "Last Name",
        validators=[DataRequired(message="Last name is required")],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address"),
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Password is required")]
    )
    role = SelectField(
        "Role",
        choices=[("user", "User"), ("admin", "Admin")],
        validators=[DataRequired(message="Please select a role")],
    )


class AdminCreateRoomForm(FlaskForm):
    roomname = StringField(
        "Room Name",
        validators=[DataRequired(message="Room name is required")],
    )
    floor = StringField(
        "Floor",
        validators=[DataRequired(message="Floor is required")],
    )


class ReplyTicketForm(FlaskForm):
    reply = TextAreaField(
        "Reply", validators=[DataRequired(message="Reply message is required")]
    )
