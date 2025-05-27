from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import StaffUser, PatronUser
from app.utils.db import db
from app.utils.extensions import bcrypt
from sqlalchemy import text

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ------------------------------------------
# REGISTER ROUTE
# ------------------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def unified_register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Hash the password securely
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        db.session.execute(text("""
            INSERT INTO patron (first_name, last_name, email, phone, registration_date, membership_expiry, is_active, password_hash)
            VALUES (:first_name, :last_name, :email, :phone, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR), 1, :password_hash)
        """), {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'password_hash': hashed_password
        })
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.unified_login'))

    return render_template('auth/register.html')


# ------------------------------------------
# LOGIN ROUTE
# ------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def unified_login():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form['email']
        password = request.form['password']
        print("Form role_type:", role)
        print("Submitted email:", email)
        print("Result:", password)

        # Determine query by role
        if role == 'patron':
            query = "SELECT * FROM patron WHERE email = :email"
        elif role in ['librarian', 'admin']:
            query = "SELECT * FROM staff WHERE email = :email"
        else:
            flash("Invalid role selected.", "danger")
            return redirect(url_for('auth.unified_login'))

        user = db.session.execute(text(query), {'email': email}).fetchone()

        # Validate user and password
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if role == 'patron':
                if not user.is_active:
                    flash("Your patron account is inactive. Please contact the library.", "warning")
                    return redirect(url_for('auth.unified_login'))
                login_user(PatronUser(
                    id=user.patron_id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name
                ))
                return redirect(url_for('patron.patron_dashboard'))

            else:
                if not user.is_active:
                    flash("Your staff account is inactive. Contact your admin.", "warning")
                    return redirect(url_for('auth.unified_login'))
                login_user(StaffUser(user.staff_id, user.email, user.role))

                # Redirect based on staff role
                if user.role == 'ADMIN':
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('staff.staff_dashboard'))

        flash("Invalid email or password.", "danger")


    return render_template('auth/login.html')


# ------------------------------------------
# LOGOUT ROUTE
# ------------------------------------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.unified_login'))
