from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    userid = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    fname = db.Column(db.Text, nullable=False)
    lname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False, default="user")

    bookings = db.relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )
    support_tickets = db.relationship(
        "SupportTicket",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="SupportTicket.userid",
    )

    __table_args__ = (
        db.CheckConstraint("role IN ('user', 'admin')", name="check_role"),
    )

    def __repr__(self):
        return f"<User {self.fname} {self.lname}>"


class Room(db.Model):
    __tablename__ = "rooms"

    roomid = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    floor = db.Column(db.Integer, nullable=False)
    roomname = db.Column(db.Text, nullable=False)
    bookings = db.relationship(
        "Booking", back_populates="room", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Room {self.roomname} (Floor {self.floor})>"


class Booking(db.Model):
    bookingid = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    userid = db.Column(
        db.Integer,
        db.ForeignKey("users.userid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    roomid = db.Column(
        db.Integer,
        db.ForeignKey("rooms.roomid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timebegin = db.Column(
        db.Text, nullable=False, default=lambda: datetime.now().isoformat()
    )
    timefinish = db.Column(db.Text)

    # Relationships
    user = db.relationship("User", back_populates="bookings")
    room = db.relationship("Room", back_populates="bookings")

    def __repr__(self):
        return f"<Booking {self.bookingid} - Room {self.roomid}>"


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"

    ticketid = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    userid = db.Column(
        db.Integer,
        db.ForeignKey("users.userid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    adminid = db.Column(
        db.Integer,
        db.ForeignKey("users.userid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    subject = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.Text, nullable=False, default=lambda: datetime.now().isoformat()
    )
    replies = db.Column(db.Text, nullable=False, default="[]")
    status = db.Column(db.Text, nullable=False, default="open")

    # Relationships
    user = db.relationship(
        "User", back_populates="support_tickets", foreign_keys=[userid]
    )
    admin = db.relationship("User", foreign_keys=[adminid])

    def __repr__(self):
        return f"<SupportTicket {self.ticketid} - {self.subject}>"
