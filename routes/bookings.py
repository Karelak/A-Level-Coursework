from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, Room, Booking
from utils.helpers import is_logged_in, get_current_user, quicksort
from forms import BookingForm, SearchSortForm

bookings_bp = Blueprint("bookings", __name__)


@bookings_bp.route("/bookings")
def bookings():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    form = SearchSortForm()
    form.sort.choices = [
        ("room_date", "Room, Date"),
        ("date", "Date"),
        ("room", "Room"),
    ]

    user_bookings = Booking.query.filter_by(userid=user.userid).all()

    # Handle search
    search_query = request.args.get("search", "").strip()
    if search_query:
        user_bookings = [
            b
            for b in user_bookings
            if search_query.lower() in (b.room.roomname if b.room else "").lower()
        ]

    # Handle sort
    sort_by = request.args.get("sort", "room_date")
    if sort_by == "room_date":
        sorted_bookings = quicksort(
            user_bookings,
            key_func=lambda booking: (
                booking.room.roomname if booking.room is not None else "",
                booking.timebegin,
            ),
        )
    elif sort_by == "date":
        sorted_bookings = quicksort(
            user_bookings, key_func=lambda booking: (booking.timebegin,)
        )
    elif sort_by == "room":
        sorted_bookings = quicksort(
            user_bookings,
            key_func=lambda booking: (
                booking.room.roomname if booking.room is not None else "",
            ),
        )
    else:
        sorted_bookings = user_bookings

    return render_template(
        "bookings/list.html",
        user=user,
        bookings=sorted_bookings,
        form=form,
        current_search=search_query,
        current_sort=sort_by,
    )


@bookings_bp.route("/bookings/new", methods=["GET", "POST"])
def new_booking():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    form = BookingForm()

    # Populate room choices
    rooms = Room.query.all()
    rooms_sorted = quicksort(
        rooms,
        key_func=lambda room: (room.roomname,),
    )
    form.roomid.choices = [
        (room.roomid, f"{room.roomname} (Floor {room.floor})") for room in rooms_sorted
    ]

    if form.validate_on_submit():
        # Validate booking duration (custom validation)
        try:
            form.validate_duration()
        except Exception as e:
            flash(str(e), "error")
            return render_template("bookings/new.html", user=user, form=form)

        # Check for conflicts
        conflicts = Booking.query.filter(
            Booking.roomid == form.roomid.data,
            Booking.timebegin < form.timefinish.data,
            Booking.timefinish > form.timebegin.data,
        ).first()

        if conflicts:
            flash("This room is already booked for the selected time", "error")
            return render_template("bookings/new.html", user=user, form=form)

        try:
            booking = Booking(
                userid=user.userid,
                roomid=form.roomid.data,
                timebegin=form.timebegin.data.isoformat(),
                timefinish=form.timefinish.data.isoformat(),
            )
            db.session.add(booking)
            db.session.commit()
            flash("Booking created successfully", "success")
            return redirect(url_for("bookings.bookings"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating booking: {str(e)}", "error")
            return render_template("bookings/new.html", user=user, form=form)

    return render_template("bookings/new.html", user=user, form=form)


@bookings_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    user = get_current_user()
    booking = Booking.query.get_or_404(booking_id)

    if booking.userid != user.userid and user.role != "admin":
        flash("You can only cancel your own bookings", "error")
        return redirect(url_for("bookings.bookings"))

    db.session.delete(booking)
    db.session.commit()
    flash("Booking cancelled successfully", "success")

    return redirect(url_for("bookings.bookings"))
