# app/routes/staff.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import datetime
from app.utils.decorators import staff_required

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import text
from app.utils.decorators import staff_required
from app.utils.db import db

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')
@staff_bp.route('/dashboard')
@login_required
@staff_required
def staff_dashboard():
    staff_id = int(current_user.id.replace("staff-", ""))

    # Get the branch_id of the staff
    branch_id = db.session.execute(
        text("SELECT branch_id FROM staff WHERE staff_id = :sid"),
        {'sid': staff_id}
    ).scalar()

    if not branch_id:
        flash("Branch not found for staff.", "danger")
        return redirect(url_for("auth.unified_login"))

    # Get summary from the view
    summary = db.session.execute(
        text("SELECT * FROM vw_branch_summary WHERE branch_id = :bid"),
        {'bid': branch_id}
    ).mappings().first()

    summary = summary or {
        'total_books': 0,
        'available_books': 0,
        'borrowed_books': 0,
        'reserved_books': 0,
        'overdue_books': 0,
        'distinct_genres': 0
    }

    # Loan activity data for chart
    loan_chart_result = db.session.execute(
        text("""
            SELECT DATE(checkout_date) AS date, COUNT(*) AS count
            FROM loan l
            JOIN book_item bi ON l.book_item_id = bi.book_item_id
            WHERE bi.branch_id = :bid
            GROUP BY date
            ORDER BY date DESC
            LIMIT 7
        """),
        {'bid': branch_id}
    ).fetchall()

    loan_chart = {
        "labels": [str(r.date) for r in reversed(loan_chart_result)],
        "values": [r.count for r in reversed(loan_chart_result)]
    }

    # Genre distribution
    genre_result = db.session.execute(
        text("""
            SELECT g.name AS genre, COUNT(*) AS count
            FROM book_item bi
            JOIN book_genre bg ON bi.book_id = bg.book_id
            JOIN genre g ON bg.genre_id = g.genre_id
            WHERE bi.branch_id = :branch_id
            GROUP BY g.name
        """),
        {'branch_id': branch_id}
    ).fetchall()

    genre_data = {
        "labels": [row.genre for row in genre_result],
        "values": [row.count for row in genre_result]
    }

    # Status breakdown (borrowed, available, etc.)
    status_result = db.session.execute(
        text("""
            SELECT status, COUNT(*) AS count
            FROM book_item
            WHERE branch_id = :branch_id
            GROUP BY status
        """),
        {'branch_id': branch_id}
    ).fetchall()

    status_data = {
        "labels": [row.status for row in status_result],
        "values": [row.count for row in status_result]
    }

    return render_template(
        'staff/dashboard.html',
        **summary,
        loan_chart=loan_chart,
        genre_data=genre_data,
        status_data=status_data
    )



@staff_bp.route('/book-management')
@login_required
@staff_required
def book_management():
    search_term = request.args.get('search', '')

    # Get filtered book list from the view (convert Row to dict for JSON)
    result = db.session.execute(
        text("""
            SELECT * FROM vw_available_books
            WHERE title LIKE :term OR authors LIKE :term OR genres LIKE :term
        """), {'term': f'%{search_term}%'}
    )
    books = [dict(row._mapping) for row in result]

    # Get all branches (for dropdowns or future admin features)
    branches = db.session.execute(text("""
        SELECT branch_id, name FROM branch
    """)).fetchall()

    return render_template('staff/books.html', books=books, branches=branches)


@staff_bp.route('/book/submit', methods=['POST'])
@login_required
@staff_required
def submit_book_form():
    form = request.form
    staff_id = int(current_user.id.replace("staff-", ""))

    # Get the branch for the current staff
    staff = db.session.execute(text("""
        SELECT branch_id FROM staff WHERE staff_id = :sid
    """), {'sid': staff_id}).fetchone()

    if not staff:
        flash("Staff not found or unauthorized.", "danger")
        return redirect(url_for('staff.book_management'))

    branch_id = staff.branch_id

    # Extract form data
    book_id = form.get('book_id')  # None for add, filled for edit
    title = form['title']
    isbn = form['isbn']
    authors = [a.strip() for a in form['authors'].split(',') if a.strip()]
    genres = [g.strip() for g in form['genres'].split(',') if g.strip()]
    copies = int(form.get('copies', 0))  # Copies only matter for add

    publication_year = int(form.get('publication_year') or 0) or None
    language = form.get('language') or None
    num_pages = int(form.get('num_pages') or 0) or None

    try:
        if not book_id:
            # === ADD NEW BOOK ===
            result = db.session.execute(text("""
                INSERT INTO book (title, isbn, publication_year, language, num_pages)
                VALUES (:title, :isbn, :pub_year, :lang, :pages)
            """), {
                'title': title,
                'isbn': isbn,
                'pub_year': publication_year,
                'lang': language,
                'pages': num_pages
            })
            db.session.commit()
            new_book_id = result.lastrowid

            # Insert authors
            for author in authors:
                names = author.split()
                first = names[0]
                last = ' '.join(names[1:]) if len(names) > 1 else ''
                a = db.session.execute(text("""
                    SELECT author_id FROM author WHERE first_name = :first AND last_name = :last
                """), {'first': first, 'last': last}).fetchone()

                aid = a.author_id if a else db.session.execute(
                    text("INSERT INTO author (first_name, last_name) VALUES (:first, :last)"),
                    {'first': first, 'last': last}).lastrowid
                if not a:
                    db.session.commit()

                db.session.execute(text("""
                    INSERT INTO book_author (book_id, author_id) VALUES (:bid, :aid)
                """), {'bid': new_book_id, 'aid': aid})

            # Insert genres
            for genre in genres:
                g = db.session.execute(text("""
                    SELECT genre_id FROM genre WHERE name = :g
                """), {'g': genre}).fetchone()

                gid = g.genre_id if g else db.session.execute(
                    text("INSERT INTO genre (name) VALUES (:g)"),
                    {'g': genre}).lastrowid
                if not g:
                    db.session.commit()

                db.session.execute(text("""
                    INSERT INTO book_genre (book_id, genre_id) VALUES (:bid, :gid)
                """), {'bid': new_book_id, 'gid': gid})

            # Insert copies
            for _ in range(copies):
                db.session.execute(text("""
                    INSERT INTO book_item (book_id, branch_id, barcode, shelf_location, acquisition_date, status)
                    VALUES (:bid, :br, UUID(), 'A1', CURDATE(), 'AVAILABLE')
                """), {'bid': new_book_id, 'br': branch_id})

            db.session.commit()
            flash("Book added successfully to your branch.", "success")

        else:
            # === EDIT EXISTING BOOK ===
            db.session.execute(text("""
                UPDATE book
                SET title = :title,
                    isbn = :isbn,
                    publication_year = :pub_year,
                    language = :lang,
                    num_pages = :pages
                WHERE book_id = :bid
            """), {
                'title': title,
                'isbn': isbn,
                'pub_year': publication_year,
                'lang': language,
                'pages': num_pages,
                'bid': book_id
            })

            # Replace authors
            db.session.execute(text("DELETE FROM book_author WHERE book_id = :bid"), {'bid': book_id})
            for author in authors:
                names = author.split()
                first = names[0]
                last = ' '.join(names[1:]) if len(names) > 1 else ''
                a = db.session.execute(text("""
                    SELECT author_id FROM author WHERE first_name = :first AND last_name = :last
                """), {'first': first, 'last': last}).fetchone()

                aid = a.author_id if a else db.session.execute(
                    text("INSERT INTO author (first_name, last_name) VALUES (:first, :last)"),
                    {'first': first, 'last': last}).lastrowid
                if not a:
                    db.session.commit()

                db.session.execute(text("""
                    INSERT INTO book_author (book_id, author_id) VALUES (:bid, :aid)
                """), {'bid': book_id, 'aid': aid})

            # Replace genres
            db.session.execute(text("DELETE FROM book_genre WHERE book_id = :bid"), {'bid': book_id})
            for genre in genres:
                g = db.session.execute(text("""
                    SELECT genre_id FROM genre WHERE name = :g
                """), {'g': genre}).fetchone()

                gid = g.genre_id if g else db.session.execute(
                    text("INSERT INTO genre (name) VALUES (:g)"),
                    {'g': genre}).lastrowid
                if not g:
                    db.session.commit()

                db.session.execute(text("""
                    INSERT INTO book_genre (book_id, genre_id) VALUES (:bid, :gid)
                """), {'bid': book_id, 'gid': gid})

            # Handle copy update
            current_total = db.session.execute(text("""
                SELECT COUNT(*) FROM book_item WHERE book_id = :bid
            """), {'bid': book_id}).scalar()

            if copies > current_total:
                to_add = copies - current_total
                for _ in range(to_add):
                    db.session.execute(text("""
                        INSERT INTO book_item (book_id, branch_id, barcode, shelf_location, acquisition_date, status)
                        VALUES (:bid, :br, UUID(), 'A1', CURDATE(), 'AVAILABLE')
                    """), {'bid': book_id, 'br': branch_id})
            elif copies < current_total:
                flash(f"Current total is {current_total}. To reduce copies, retire them manually.", "warning")

        db.session.commit()
        flash("Book updated successfully.", "success")
            
    except Exception as e:
        db.session.rollback()
        flash(f"Error while saving book: {str(e)}", "danger")

    return redirect(url_for('staff.book_management'))

@staff_bp.route('/book/<int:book_id>/items')
@login_required
@staff_required
def get_book_items(book_id):
    rows = db.session.execute(text("""
        SELECT book_item_id, status
        FROM book_item
        WHERE book_id = :bid
        ORDER BY book_item_id
    """), {'bid': book_id}).fetchall()
    
    return jsonify(items=[dict(row._mapping) for row in rows])

@staff_bp.route('/book/item/update-status', methods=['POST'])
@login_required
@staff_required
def update_book_item_status():
    item_id = request.form.get('book_item_id')
    new_status = request.form.get('status')

    try:
        db.session.execute(text("""
            UPDATE book_item
            SET status = :status
            WHERE book_item_id = :id
        """), {'status': new_status, 'id': item_id})
        db.session.commit()
        flash("Book item status updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating status: {str(e)}", "danger")

    return redirect(url_for('staff.book_management'))


# --- Circulation Management UI ---
@staff_bp.route('/circulation')
@login_required
@staff_required
def circulation():
    reservations = db.session.execute(text("""
        SELECT * FROM vw_pending_reservations
    """)).fetchall()

    loans = db.session.execute(text("""
        SELECT loan_id, book_title,
            patron_name, checkout_date, due_date, loan_status AS status
        FROM vw_patron_loans
        WHERE loan_status IN ('CURRENT', 'OVERDUE')
    """)).fetchall()

    return render_template('staff/circulation.html', reservations=reservations, loans=loans)

# --- Approve Reservation ---
@staff_bp.route('/approve-reservation', methods=['POST'])
@login_required
@staff_required
def approve_reservation():
    reservation_id = request.form.get('reservation_id')

    db.session.execute(text("""
        UPDATE reservation
        SET status = 'FULFILLED'
        WHERE reservation_id = :rid AND status = 'PENDING'
    """), {'rid': reservation_id})
    db.session.commit()

    flash("Reservation approved successfully.", "success")
    return redirect(url_for('staff.circulation'))

# --- Decline Reservation ---
@staff_bp.route('/decline-reservation', methods=['POST'])
@login_required
@staff_required
def decline_reservation():
    reservation_id = request.form.get('reservation_id')

    db.session.execute(text("""
        UPDATE reservation
        SET status = 'CANCELLED'
        WHERE reservation_id = :rid AND status = 'PENDING'
    """), {'rid': reservation_id})
    db.session.commit()

    flash("Reservation declined.", "info")
    return redirect(url_for('staff.circulation'))

# --- Return Book ---
@staff_bp.route('/return-book', methods=['POST'])
@login_required
@staff_required
def return_book():
    staff_id = int(current_user.id.replace("staff-", ""))

    loan_id = request.form.get('loan_id')

    db.session.execute(text("""
        UPDATE loan
        SET return_date = NOW(),
            status = CASE 
                        WHEN due_date < CURDATE() THEN 'OVERDUE'
                        ELSE 'RETURNED'
                     END,
            returning_staff_id = :sid
        WHERE loan_id = :lid AND status IN ('CURRENT', 'OVERDUE')
    """), {'lid': loan_id, 'sid': staff_id})
    db.session.commit()

    flash("Book return processed.", "success")
    return redirect(url_for('staff.circulation', tab='returns'))

# --- Patron Management ---
@staff_bp.route('/patrons')
@login_required
@staff_required
def patron():
    patrons = db.session.execute(text("""
        SELECT patron_id, first_name, last_name, email, phone,
               membership_expiry, is_active
        FROM patron
        ORDER BY last_name, first_name
    """)).fetchall()
    return render_template('staff/patrons.html', patrons=patrons)

@staff_bp.route('/toggle-patron-status', methods=['POST'])
@login_required
@staff_required
def toggle_patron_status():
    patron_id = request.form.get('patron_id')
    db.session.execute(text("""
        UPDATE patron
        SET is_active = NOT is_active
        WHERE patron_id = :pid
    """), {'pid': patron_id})
    db.session.commit()
    flash("Patron status updated successfully.", "success")
    return redirect(request.referrer or url_for('staff.patron_management'))


@staff_bp.route('/patron/<int:patron_id>/detail')
@staff_required
def patron_detail_modal(patron_id):
    result = db.session.execute(text("""
        SELECT
            book_title,
            checkout_date,
            due_date,
            return_date,
            loan_status,
            fine_amount,
            IFNULL(payment_status, 'N/A') AS payment_status
        FROM vw_patron_loans
        WHERE patron_id = :pid
        ORDER BY checkout_date DESC
    """), {'pid': patron_id}).fetchall()
    return render_template('staff/_patron_detail_modal.html', records=result)
