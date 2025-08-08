from flask import render_template, jsonify
from flask_login import login_required
from app.main import bp
from app import db

@bp.route('/')
@bp.route('/index')
def index():
    # For now, just render a simple template
    return render_template('main/index.html', title='Home')

@bp.route('/account')
@login_required
def account():
    """User account page."""
    return render_template('main/account.html', title='My Account')

@bp.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
