# Routes for patron homepage after login

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Loan, Fine
from app.utils.decorators import patron_required
from app.utils.db import db

patron_bp = Blueprint('patron', __name__)

@patron_bp.route('/patron/dashboard')
@login_required
@patron_required

def patron_dashboard():
    user_id = current_user.id

    # Aggregate loan/fine data for minicards
    total_loans = Loan.query.filter_by(patron_id=user_id).count()
    returned_loans = Loan.query.filter_by(patron_id=user_id, status='RETURNED').count()
    current_loans = Loan.query.filter_by(patron_id=user_id, status='CURRENT').count()
    overdue_loans = Loan.query.filter_by(patron_id=user_id, status='OVERDUE').count()

    unpaid_fines = (
        db.session.query(Fine)
        .join(Loan, Fine.loan_id == Loan.loan_id)
        .filter(Loan.patron_id == user_id, Fine.payment_status == 'PENDING')
        .count()
    )

    return render_template(
        'patron/dashboard.html',
        current_loans=current_loans,
        overdue_loans=overdue_loans,
        unpaid_fines=unpaid_fines,
        total_loans=total_loans,
        returned_loans=returned_loans
    )
