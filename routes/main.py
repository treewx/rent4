from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.user import User
from models.property import Property
from app import login_manager

main_bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    properties = Property.query.filter_by(user_id=current_user.id).all()
    property_count = len(properties)

    return render_template('dashboard.html',
                           properties=properties,
                           property_count=property_count,
                           can_add_property=current_user.can_add_property(),
                           property_limit=current_user.get_property_limit())

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')