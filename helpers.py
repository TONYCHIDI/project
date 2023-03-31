from flask import redirect, render_template, request, session
from functools import wraps


"""Render an error message to user."""
def error(message, code=400):
    def escape(s):
        """
        Escape special characters.

        Copied from CS50 finance task
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("error.html", top=code, bottom=escape(message)), code


"""
Decorate routes to require login.

Copied from CS50 finance task
"""
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


"""Format value as Naira."""
def NGN(value):
    return f"\u20A6{value:,.2f}"
