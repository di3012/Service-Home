# utils.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user as flask_login_user, logout_user as flask_logout_user, current_user
from functools import wraps
from flask import redirect, url_for, flash

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

def login_user(user):
    flask_login_user(user)

def logout_user():
    flask_logout_user()

def require_role(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash("Unauthorized access.", "error")
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper