# Routes for patron homepage after login

from flask import Blueprint, render_template, redirect, url_for, flash, request
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
@patron_required
def my_books():
    patron_id = int(current_user.id.split('-')[1])
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM vw_patron_loans WHERE patron_id = :pid AND loan_status IN ('CURRENT', 'OVERDUE')"), {'pid': patron_id})        
    borrowed_loans = PatronLoanView.query.filter(
        PatronLoanView.patron_id == patron_id,
        PatronLoanView.loan_status.in_(['CURRENT', 'OVERDUE'])
    ).all()

    returned_loans = PatronLoanView.query.filter(
        PatronLoanView.patron_id == patron_id,
        PatronLoanView.loan_status == 'RETURNED'
    ).all()
    
    reservations = db.session.execute(text("""
        SELECT r.reservation_id, b.title, r.reservation_date, r.expiry_date, r.status
        FROM reservation r
        JOIN book b ON r.book_id = b.book_id
        WHERE r.patron_id = :pid AND r.status = 'PENDING'
        ORDER BY r.reservation_date DESC
    """), {'pid': patron_id}).fetchall()   

    return render_template('patron/my_books.html',
                           borrowed_loans=borrowed_loans,
                           returned_loans=returned_loans,
                           reservations=reservations)


@patron_bp.route('/patron/catalog', methods=['GET'])
@login_required
@patron_required
def catalog():
    search_query = request.args.get('q', '').strip()

    sql = """
        SELECT 
            book_id,
            title,
            authors,
            genres,
            branch_name
        FROM vw_available_books
    """

    params = {}
    if search_query:
        sql += """
            WHERE 
                title LIKE :query OR
                authors LIKE :query OR
                genres LIKE :query
        """
        params['query'] = f"%{search_query}%"

    sql += " ORDER BY book_id ASC"

    result = db.session.execute(text(sql), params)
    books = result.fetchall()

    return render_template('patron/catalog.html', books=books)


@patron_bp.route('/patron/reserve', methods=['POST'])
@login_required
@patron_required
def reserve_book():
    book_id = request.form.get('book_id')
    patron_id = int(current_user.id.split('-')[1])

    # Prevent duplicate reservations for same book & patron
    existing = db.session.execute(text("""
        SELECT 1 FROM reservation 
        WHERE patron_id = :patron_id AND book_id = :book_id AND status = 'PENDING'
    """), {'patron_id': patron_id, 'book_id': book_id}).fetchone()

    if existing:
        flash("You already have a pending reservation for this book.", "warning")
        return redirect(url_for('patron.catalog'))

    try:
        db.session.execute(text("""
            INSERT INTO reservation (book_id, patron_id, reservation_date, expiry_date, status)
            VALUES (:book_id, :patron_id, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), 'PENDING')
        """), {'book_id': book_id, 'patron_id': patron_id})
        db.session.commit()
        flash("Your reservation was successfully submitted.", "success")
    except Exception as e:
        db.session.rollback()
        print("[ERROR] Reservation failed:", e)  # Add this line
        flash("Reservation failed. Please try again.", "danger")


    return redirect(url_for('patron.catalog'))

@patron_bp.route('/patron/cancel-reservation', methods=['POST'])
@login_required
@patron_required
def cancel_reservation():
    reservation_id = request.form.get('reservation_id')
    patron_id = int(current_user.id.split('-')[1])  
    try:
        result = db.session.execute(text("""
            UPDATE reservation
            SET status = 'CANCELLED'
            WHERE reservation_id = :id AND patron_id = :pid AND status = 'PENDING'
        """), {'id': reservation_id, 'pid': patron_id})
        db.session.commit()

        if result.rowcount == 0:
            flash("Reservation not found or already cancelled.", "warning")
        else:
            flash("Reservation cancelled successfully.", "success")

    except Exception as e:
        db.session.rollback()
        print("[ERROR] Cancel failed:", e)
        flash("Failed to cancel reservation.", "danger")

    return redirect(url_for('patron.my_books', tab='reserved'))


