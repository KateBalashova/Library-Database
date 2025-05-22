# Custom role-based access control decorators

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(current_user, 'role') or current_user.role not in roles:
                flash("Unauthorized access.")
                return redirect(url_for('auth.staff_login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

def patron_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'patron':
            flash("Only patrons allowed.")
            return redirect(url_for('auth.unified_login'))
        return f(*args, **kwargs)
    return wrapper

    
