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

    # Relationship
    loans = db.relationship('Loan', backref='patron', lazy=True)

class Loan(db.Model):
    __tablename__ = 'loan'
    loan_id = db.Column(db.Integer, primary_key=True)
    book_item_id = db.Column(db.Integer, db.ForeignKey('book_item.book_item_id'), nullable=False)
    book_item = db.relationship('BookItem', backref='loans')
    issuing_staff_id = db.Column(db.Integer)
    returning_staff_id = db.Column(db.Integer)
    checkout_date = db.Column(db.DateTime)
    due_date = db.Column(db.Date)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.Enum('CURRENT', 'RETURNED', 'OVERDUE', 'LOST', name='loan_status'))

    # Relationship
    fines = db.relationship('Fine', backref='loan', lazy=True)

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

