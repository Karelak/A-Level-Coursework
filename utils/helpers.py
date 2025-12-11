from flask import session
from utils.models import db, User


def is_logged_in():
    return "userid" in session


def get_current_user():
    if is_logged_in():
        return db.session.get(User, session["userid"])
    return None


def sorter(items, key_func):
    if len(items) <= 1:
        return items

    pivot = items[len(items) // 2]
    left = [item for item in items if key_func(item) < key_func(pivot)]
    middle = [item for item in items if key_func(item) == key_func(pivot)]
    right = [item for item in items if key_func(item) > key_func(pivot)]

    return sorter(left, key_func) + middle + sorter(right, key_func)
