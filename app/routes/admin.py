from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import text, func
from datetime import datetime

from app.utils.decorators import admin_required
from app.utils.db import db

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin dashboard
@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Patron Management
@admin_bp.route('/patrons')
@login_required
@admin_required
def patrons():
    return render_template('admin/patron_management.html')

# Branch Management
@admin_bp.route('/branches')
@login_required
@admin_required
def branches():
    return render_template('admin/branch_management.html')

# Staff Management
@admin_bp.route('/staff')
@login_required
@admin_required
def staff():
    staff_query = text("""
        SELECT s.staff_id, s.first_name, s.last_name, s.email, s.role, s.is_active,
               b.name AS branch_name
        FROM staff s
        JOIN branch b ON s.branch_id = b.branch_id
        ORDER BY s.role, s.last_name
    """)
    branch_query = text("SELECT branch_id, name FROM branch")

    staff_list = db.session.execute(staff_query).mappings().all()
    branches = db.session.execute(branch_query).mappings().all()

    return render_template('admin/staff_management.html', 
                           staff_list=staff_list, 
                           branches=branches)


@admin_bp.route('/staff/create', methods=['POST'])
@login_required
@admin_required
def create_staff():
    from flask import request, redirect, flash
    from app.utils.extensions import bcrypt

    data = request.form
    try:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        insert_query = text("""
            INSERT INTO staff (branch_id, first_name, last_name, email, phone, role, password_hash, hire_date, is_active)
            VALUES (:branch_id, :first_name, :last_name, :email, :phone, :role, :password_hash, CURDATE(), TRUE)
        """)

        db.session.execute(insert_query, {
            'branch_id': data['branch_id'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'phone': data['phone'],
            'role': data['role'],
            'password_hash': hashed_pw
        })
        db.session.commit()
        flash("Staff account created successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to create staff: {str(e)}", "danger")

    return redirect(url_for('admin.staff'))

# System Settings
@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    return render_template('admin/system_settings.html')

@admin_bp.route('/debug-user')
def debug_user():
    from flask_login import current_user
    return {
        "is_authenticated": current_user.is_authenticated,
        "id": current_user.get_id(),
        "role": getattr(current_user, 'role', 'N/A')
    }