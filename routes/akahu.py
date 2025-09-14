from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db

akahu_bp = Blueprint('akahu', __name__, url_prefix='/akahu')

@akahu_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    if request.method == 'POST':
        app_token = request.form.get('app_token', '').strip()
        user_token = request.form.get('user_token', '').strip()

        if not app_token or not user_token:
            flash('Please enter both App Token and User Token.', 'error')
            return render_template('akahu/setup.html')

        # Update user's Akahu tokens
        current_user.akahu_app_token = app_token
        current_user.akahu_user_token = user_token
        db.session.commit()

        flash('Akahu integration configured successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('akahu/setup.html')