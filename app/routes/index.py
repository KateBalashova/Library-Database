from flask import Blueprint, redirect, url_for

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    return redirect(url_for('auth.unified_login'))
