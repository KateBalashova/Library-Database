import sys
import os
from sqlalchemy import text

# Add the parent directory (one level up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.utils.db import db


app = create_app()

with app.app_context():
    try:
        result = db.session.execute(text("SELECT 1"))
        print("Connection to MySQL successful! Result:", result.scalar())
    except Exception as e:
        print("Connection failed:", e)
