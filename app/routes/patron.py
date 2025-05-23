# Routes for patron homepage after login

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text, func
from datetime import datetime

from app.models import Book, BookGenre, Genre, PatronLoanView
from app.utils.decorators import patron_required
from app.utils.db import db

patron_bp = Blueprint('patron', __name__)

@patron_bp.route('/patron/dashboard')
@login_required
@patron_required

def patron_dashboard():
    patron_id = int(current_user.id.split('-')[1])


    # For Data cards:
    # Borrowed books
    loan_stats_query = text("""
        SELECT 
            SUM(CASE WHEN loan_status = 'CURRENT' THEN 1 ELSE 0 END) AS current,
            SUM(CASE WHEN loan_status = 'RETURNED' THEN 1 ELSE 0 END) AS returned,
            SUM(CASE WHEN loan_status = 'OVERDUE' THEN 1 ELSE 0 END) AS overdue
        FROM vw_patron_loans
        WHERE patron_id = :pid
    """)
    stats_result = db.session.execute(loan_stats_query, {'pid': patron_id}).fetchone()
    current_count, returned_count, overdue_count = stats_result or (0, 0, 0)
    borrowed_count = current_count + returned_count + overdue_count
    
    # For Fine Amount
    fine_query = text("""
        SELECT SUM(fine_amount)
        FROM vw_patron_loans
        WHERE patron_id = :pid AND payment_status = 'PENDING'
    """)
    fine_amount = db.session.execute(fine_query, {'pid': patron_id}).scalar() or 0

    # For Pie chart
    return_ratio_data = {
        'labels': ['Returned', 'Current', 'Overdue'],
        'values': [returned_count, current_count, overdue_count]
    }
    
    # For Book Genres
    genre_query = text("""
        SELECT genres
        FROM vw_patron_loans
        WHERE patron_id = :pid
    """)
    rows = db.session.execute(genre_query, {'pid': patron_id}).fetchall()

    # Parse genre names into a flat list
    from collections import Counter
    genre_counter = Counter()
    for row in rows:
        if row[0]:
            genres = [g.strip() for g in row[0].split(',')]
            genre_counter.update(genres)

    genre_data = {
        'labels': list(genre_counter.keys()),
        'values': list(genre_counter.values())
    }
    
    # For book activities
    time_query = text("""
        SELECT DATE(checkout_date) AS borrow_date, COUNT(*) AS total
        FROM vw_patron_loans
        WHERE patron_id = :pid
        GROUP BY borrow_date
        ORDER BY borrow_date ASC
    """)
    time_result = db.session.execute(time_query, {'pid': patron_id}).fetchall()
    chart_data = {
        'labels': [row[0].strftime("%Y-%m-%d") for row in time_result],
        'values': [row[1] for row in time_result]
    }

    return render_template('patron/dashboard.html',
                           borrowed_count=borrowed_count,
                           returned_count=returned_count,
                           overdue_count=overdue_count,
                           fine_amount=fine_amount,
                           current_time=datetime.now().strftime("%I:%M %p"),
                           current_date=datetime.now().strftime("%b %d, %Y"),
                           chart_data=chart_data,
                           genre_data=genre_data,
                           return_ratio_data=return_ratio_data)
    
@patron_bp.route('/mybooks')
@login_required  
def my_books():
    patron_id = int(current_user.id.split('-')[1])

    borrowed_loans = PatronLoanView.query.filter(
        PatronLoanView.patron_id == patron_id,
        PatronLoanView.loan_status.in_(['CURRENT', 'OVERDUE'])
    ).all()

    returned_loans = PatronLoanView.query.filter(
        PatronLoanView.patron_id == patron_id,
        PatronLoanView.loan_status == 'RETURNED'
    ).all()

    return render_template('patron/my_books.html',
                           borrowed_loans=borrowed_loans,
                           returned_loans=returned_loans)

