# Routes for patron homepage after login

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text, func
from datetime import datetime

from app.models import Loan, Book, BookGenre, Genre
from app.utils.decorators import patron_required
from app.utils.db import db

patron_bp = Blueprint('patron', __name__)

@patron_bp.route('/patron/dashboard')
@login_required
@patron_required

def patron_dashboard():
    patron_id = int(current_user.id.split('-')[1])


    # For Data cards
    current_query = text("""
        SELECT COUNT(*) FROM loan 
        WHERE patron_id = :pid AND status = 'CURRENT'
    """)

    returned_query = text("""
        SELECT COUNT(*) FROM loan
        WHERE patron_id = :pid AND status = 'RETURNED'
    """)
    overdue_query = text("""
        SELECT COUNT(*) FROM loan
        WHERE patron_id = :pid AND status = 'OVERDUE'
    """)

    fine_query = text("""
        SELECT IFNULL(SUM(f.amount), 0) FROM fine f
        JOIN loan l ON f.loan_id = l.loan_id
        WHERE l.patron_id = :pid AND f.payment_status = 'PENDING'
    """)

    
    current_count = db.session.execute(current_query, {'pid': patron_id}).scalar()
    returned_count = db.session.execute(returned_query, {'pid': patron_id}).scalar()
    overdue_count = db.session.execute(overdue_query, {'pid': patron_id}).scalar()
    fine_amount = db.session.execute(fine_query, {'pid': current_user.id}).scalar()
    borrowed_count = current_count + returned_count + overdue_count
    # For book returned over borrowed
    return_ratio_data = {
        'labels': ['Returned', 'Current', 'Overdue'],
        'values': [returned_count, current_count, overdue_count]
    }
        
    # For Book Genres
    genre_query = text("""
        SELECT g.name, COUNT(*) AS borrow_count
        FROM loan l
        JOIN book_item bi ON l.book_item_id = bi.book_item_id
        JOIN book b ON bi.book_id = b.book_id
        JOIN book_genre bg ON b.book_id = bg.book_id
        JOIN genre g ON bg.genre_id = g.genre_id
        WHERE l.patron_id = :pid
        GROUP BY g.name
    """)
    genre_result = db.session.execute(genre_query, {'pid': patron_id}).fetchall()
    genre_labels = [row[0] for row in genre_result]
    genre_values = [row[1] for row in genre_result]
    
    # For book activities
    time_query = text("""
        SELECT DATE(checkout_date) AS borrow_date, COUNT(*) AS total
        FROM loan
        WHERE patron_id = :pid
        GROUP BY borrow_date
        ORDER BY borrow_date ASC
    """)
    time_result = db.session.execute(time_query, {'pid': patron_id}).fetchall()
    time_labels = [row[0].strftime("%Y-%m-%d") for row in time_result]
    time_values = [row[1] for row in time_result]
    
    chart_data = {'labels': time_labels, 'values': time_values}
    genre_data = {'labels': genre_labels, 'values': genre_values}
    
    print("DEBUG current_user.id:", current_user.id) 
    print("DEBUG chart_data:", chart_data)
    print("DEBUG genre_data:", genre_labels, genre_values)
    print("DEBUG return_ratio_data:", return_ratio_data)
    print("DEBUG parsed patron_id:", current_user.id.split('-')[1])

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