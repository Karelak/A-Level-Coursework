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
            duration_hours = duration.total_seconds() / 3600
            if duration_hours > 8:
                raise ValidationError("Booking duration cannot exceed 8 hours")


class SupportTicketForm(FlaskForm):
    subject = StringField(
        "Subject", validators=[DataRequired(message="Subject is required")]
    )
    message = TextAreaField(
        "Message", validators=[DataRequired(message="Message is required")]
    )
