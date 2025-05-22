from flask_login import UserMixin
from sqlalchemy.sql import text
from app.utils.extensions import login_manager
from app.utils.db import db

# ---------------------------
# Login User Classes
# ---------------------------

class StaffUser(UserMixin):
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role
        self.user_type = 'staff'

class PatronUser(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email
        self.role = 'PATRON'
        self.user_type = 'patron'

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
    book_item_id = db.Column(db.Integer)
    patron_id = db.Column(db.Integer, db.ForeignKey('patron.patron_id'), nullable=False)
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

# ---------------------------
# Login Manager Loader
# ---------------------------

@login_manager.user_loader
def load_user(user_id):
    # Try staff
    result = db.session.execute(text("SELECT * FROM staff WHERE staff_id = :id"), {'id': user_id}).fetchone()
    if result:
        return StaffUser(id=result.staff_id, email=result.email, role=result.role)

    # Try patron
    result = db.session.execute(text("SELECT * FROM patron WHERE patron_id = :id"), {'id': user_id}).fetchone()
    if result:
        return PatronUser(id=result.patron_id, email=result.email)

    return None
