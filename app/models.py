from flask_login import UserMixin
from sqlalchemy.sql import text
from app.utils.extensions import login_manager
from app.utils.db import db

# ---------------------------
# Login User Classes
# ---------------------------

class StaffUser(UserMixin):
    def __init__(self, id, email, role, first_name=None, last_name=None):
        self.id = f"staff-{id}"
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.user_type = 'staff'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class PatronUser(UserMixin):
    def __init__(self, id, email, first_name=None, last_name=None):
        self.id = f"patron-{id}"
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = 'PATRON'
        self.user_type = 'patron'
        
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

# ---------------------------
# ORM Models (for queries)
# ---------------------------

class Patron(db.Model):
    __tablename__ = 'patron'
    patron_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    registration_date = db.Column(db.Date)
    membership_expiry = db.Column(db.Date)


class Loan(db.Model):
    __tablename__ = 'loan'

    loan_id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    book_item_id = db.Column(db.Integer, db.ForeignKey('book_item.book_item_id'), nullable=False)
    patron_id = db.Column(db.Integer, db.ForeignKey('patron.patron_id'), nullable=False)
    issuing_staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    returning_staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)

    # Dates
    checkout_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.DateTime)

    # Status
    status = db.Column(
        db.Enum('CURRENT', 'RETURNED', 'OVERDUE', 'LOST', name='loan_status'),
        default='CURRENT'
    )

    # Relationships
    book_item = db.relationship('BookItem', backref='loans')
    patron = db.relationship('Patron', backref='loans')
    fines = db.relationship('Fine', backref='loan', lazy=True)

    
class PatronLoanView(db.Model):
    __tablename__ = 'vw_patron_loans'
    __table_args__ = {'extend_existing': True}

    loan_id = db.Column(db.Integer, primary_key=True)
    patron_id = db.Column(db.Integer, primary_key=True)
    patron_name = db.Column(db.String(100), nullable=True)
    book_title = db.Column(db.String(255), nullable=True)
    authors = db.Column(db.String(255), nullable=True)
    genres = db.Column(db.String(255), nullable=True)
    checkout_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    loan_status = db.Column(db.Enum('CURRENT', 'RETURNED', 'OVERDUE', 'LOST'), nullable=True)
    fine_amount = db.Column(db.Numeric(10, 2), nullable=True)
    payment_status = db.Column(db.Enum('PENDING', 'PAID', 'WAIVED'), nullable=True)

    


class Fine(db.Model):
    __tablename__ = 'fine'
    fine_id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.loan_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2))
    issue_date = db.Column(db.DateTime)
    payment_status = db.Column(db.Enum('PENDING', 'PAID', 'WAIVED', name='fine_status'))
    payment_date = db.Column(db.DateTime)

class BookItem(db.Model):
    __tablename__ = 'book_item'
    book_item_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    branch_id = db.Column(db.Integer)
    status = db.Column(db.Enum('AVAILABLE', 'CHECKED_OUT', 'RESERVED', 'LOST', 'DAMAGED', 'BEING_REPAIRED', name='book_status'))

    # Relationship
    book = db.relationship('Book', backref='items')

class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    isbn = db.Column(db.String(20), unique=True)
    publication_year = db.Column(db.Integer)

class Genre(db.Model):
    __tablename__ = 'genre'
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class BookGenre(db.Model):
    __tablename__ = 'book_genre'
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.genre_id'), primary_key=True)

    genre = db.relationship('Genre', backref='book_genres')
    book = db.relationship('Book', backref='book_genres')


# ---------------------------
# Login Manager Loader
# ---------------------------


@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith("patron-"):
        id = int(user_id.split("-")[1])
        result = db.session.execute(text("SELECT * FROM patron WHERE patron_id = :id"), {'id': id}).fetchone()
        if result:
            return PatronUser(
                id=result.patron_id,
                email=result.email,
                first_name=result.first_name,
                last_name=result.last_name
            )

    elif user_id.startswith("staff-"):
        id = int(user_id.split("-")[1])
        result = db.session.execute(text("SELECT * FROM staff WHERE staff_id = :id"), {'id': id}).fetchone()
        if result:
            return StaffUser(
                id=result.staff_id,
                email=result.email,
                role=result.role,
                first_name=result.first_name,
                last_name=result.last_name
            )

    return None

