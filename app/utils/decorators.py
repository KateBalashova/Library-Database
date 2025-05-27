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
        if current_user.role != 'PATRON':
            flash("Access restricted to patrons only.", "danger")
            return redirect(url_for('auth.unified_login'))  
        return f(*args, **kwargs)
    return wrapper

    
def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['LIBRARIAN', 'MANAGER', 'ADMIN', 'ASSISTANT']:
            flash("You are not authorized to access this page.", "danger")
            return redirect(url_for('auth.unified_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function