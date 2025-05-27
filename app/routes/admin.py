from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import text, func
from datetime import datetime

from app.utils.decorators import admin_required
from app.utils.db import db

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app.utils.extensions import bcrypt  


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import text
from app.utils.db import db
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # --- Summary Cards ---
    result = db.session.execute(text("""
        SELECT 
            (SELECT COUNT(*) FROM branch) AS total_branches,
            (SELECT COUNT(*) FROM patron) AS patron_count,
            (SELECT COUNT(*) FROM staff WHERE is_active = 1) AS staff_count,
            (SELECT COUNT(*) FROM book_item) AS total_books
    """)).fetchone()

    # --- Book Distribution per Branch (vw_branch_summary) ---
    branch_summary = db.session.execute(text("""
        SELECT branch_name, total_books
        FROM vw_branch_summary
        ORDER BY branch_name
    """)).fetchall()

    branch_labels = [row.branch_name for row in branch_summary]
    branch_data = [row.total_books for row in branch_summary]

    # --- Patron Registration Growth (Last 6 months) ---
    patron_growth = db.session.execute(text("""
        SELECT DATE_FORMAT(registration_date, '%Y-%m') AS month, COUNT(*) AS new_patrons
        FROM patron
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """)).fetchall()

    # Reverse for chronological order
    patron_growth = patron_growth[::-1]
    patron_growth_labels = [row.month for row in patron_growth]
    patron_growth_values = [row.new_patrons for row in patron_growth]

    # --- Monthly Loans (Last 6 months) ---
    loan_stats = db.session.execute(text("""
        SELECT DATE_FORMAT(checkout_date, '%Y-%m') AS month, COUNT(*) AS loans
        FROM loan
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """)).fetchall()

    loan_stats = loan_stats[::-1]
    loan_labels = [row.month for row in loan_stats]
    loan_values = [row.loans for row in loan_stats]

    # --- Chart Data Dictionary ---
    chart_data = {
        "labels": branch_labels,
        "branch_data": branch_data,
        "patron_growth_labels": patron_growth_labels,
        "patron_growth_values": patron_growth_values,
        "loan_labels": loan_labels,
        "loan_values": loan_values
    }

    return render_template("admin/dashboard.html",
                           total_branches=result.total_branches,
                           patron_count=result.patron_count,
                           staff_count=result.staff_count,
                           total_books=result.total_books,
                           chart_data=chart_data)

# Patron Management
# View: Patron Management
@admin_bp.route('/patrons', methods=['GET'])
@login_required
@admin_required
def patrons():
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    query = text("""
        SELECT * FROM patron
        WHERE (first_name LIKE :search OR last_name LIKE :search OR email LIKE :search)
        AND (:status = '' OR is_active = :active_flag)
        ORDER BY registration_date DESC
    """)
    patrons_raw = db.session.execute(query, {
        'search': f'%{search}%',
        'status': status,
        'active_flag': True if status == 'active' else False
    }).fetchall()
    
    patrons = [dict(row._mapping) for row in patrons_raw]

    return render_template('admin/patron_management.html', patrons=patrons)

# Create Patron
@admin_bp.route('/create-patron', methods=['POST'])
@login_required
@admin_required
def create_patron():
    data = request.form
    try:
        default_password = 'patron@123'
        hashed_password = bcrypt.generate_password_hash(default_password).decode('utf-8')

        db.session.execute(text("""
            INSERT INTO patron (
                first_name, last_name, email, phone,
                registration_date, membership_expiry,
                max_books_allowed, password_hash
            )
            VALUES (
                :fname, :lname, :email, :phone,
                :reg_date, :exp_date,
                :max_books, :hashed
            )
        """), {
            'fname': data['first_name'],
            'lname': data['last_name'],
            'email': data['email'],
            'phone': data['phone'],
            'reg_date': data['registration_date'],
            'exp_date': data['membership_expiry'],
            'max_books': data['max_books_allowed'],
            'hashed': hashed_password
        })
        db.session.commit()
        flash("Patron created successfully with default password 'patron@123'.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating patron: {str(e)}", "danger")

    return redirect(url_for('admin.patrons'))

# Toggle Patron Active Status
@admin_bp.route('/toggle-patron-status', methods=['POST'])
@login_required
@admin_required
def toggle_patron_status():
    patron_id = request.form.get('patron_id')
    db.session.execute(text("""
        UPDATE patron SET is_active = NOT is_active WHERE patron_id = :pid
    """), {'pid': patron_id})
    db.session.commit()
    flash("Patron status updated.", "success")
    return redirect(request.referrer or url_for('admin.patrons'))

@admin_bp.route('/reset-patron-password', methods=['POST'])
@login_required
@admin_required
def reset_patron_password():
    patron_id = request.form.get('patron_id')
    default_password = 'patron@123'

    try:
        hashed_password = bcrypt.generate_password_hash(default_password).decode('utf-8')

        db.session.execute(text("""
            UPDATE patron
            SET password_hash = :pwd
            WHERE patron_id = :pid
        """), {'pwd': hashed_password, 'pid': patron_id})
        db.session.commit()

        flash("Password reset to 'patron@123'.", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"Error resetting password: {str(e)}", "danger")

    return redirect(request.referrer or url_for('admin.patrons'))

@admin_bp.route('/update-patron', methods=['POST'])
@login_required
@admin_required
def update_patron():
    data = request.form
    try:
        db.session.execute(text("""
            UPDATE patron
            SET first_name = :fname,
                last_name = :lname,
                email = :email,
                phone = :phone,
                registration_date = :reg_date,
                membership_expiry = :exp_date,
                max_books_allowed = :max_books
            WHERE patron_id = :pid
        """), {
            'fname': data['first_name'],
            'lname': data['last_name'],
            'email': data['email'],
            'phone': data['phone'],
            'reg_date': data['registration_date'],
            'exp_date': data['membership_expiry'],
            'max_books': data['max_books_allowed'],
            'pid': data['patron_id']
        })
        db.session.commit()
        flash("Patron updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating patron: {str(e)}", "danger")

    return redirect(url_for('admin.patrons'))

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
    result = db.session.execute(text("""
        SELECT 
            s.staff_id, s.first_name, s.last_name, s.email, s.phone, s.role, 
            s.branch_id, b.name AS branch_name, s.is_active
        FROM staff s
        JOIN branch b ON s.branch_id = b.branch_id
    """))

    staff_list = []
    for row in result:
        staff_list.append({
            'staff_id': row.staff_id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'email': row.email,
            'phone': row.phone,
            'role': row.role,
            'branch_id': row.branch_id,
            'branch_name': row.branch_name,
            'is_active': row.is_active
        })

    branches = db.session.execute(text("SELECT branch_id, name FROM branch")).fetchall()

    return render_template('admin/staff_management.html', staff_list=staff_list, branches=branches)


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

@admin_bp.route('/update-staff', methods=['POST'])
@login_required
@admin_required
def update_staff():
    data = request.form
    db.session.execute(text("""
        UPDATE staff
        SET first_name = :fn,
            last_name = :ln,
            phone = :phone,
            role = :role,
            branch_id = :branch
        WHERE staff_id = :sid
    """), {
        'fn': data['first_name'],
        'ln': data['last_name'],
        'phone': data['phone'],
        'role': data['role'],
        'branch': data['branch_id'],
        'sid': data['staff_id']
    })
    db.session.commit()
    flash("Staff information updated successfully.", "success")
    return redirect(url_for('admin.staff'))


@admin_bp.route('/toggle-staff-status', methods=['POST'])
@login_required
@admin_required
def toggle_staff_status():
    staff_id = request.form.get('staff_id')
    db.session.execute(text("""
        UPDATE staff
        SET is_active = NOT is_active
        WHERE staff_id = :sid
    """), {'sid': staff_id})
    db.session.commit()
    flash("Staff status updated.", "success")
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