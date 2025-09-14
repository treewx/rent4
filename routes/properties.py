from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from decimal import Decimal
from app import db
from models.property import Property
from services.email_service import EmailService

properties_bp = Blueprint('properties', __name__, url_prefix='/properties')
email_service = EmailService()

@properties_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_property():
    if not current_user.can_add_property():
        flash('You need to upgrade your account to add more properties.', 'error')
        return redirect(url_for('stripe_routes.upgrade'))

    if request.method == 'POST':
        # Get form data
        address = request.form.get('address', '').strip()
        tenant_name = request.form.get('tenant_name', '').strip()
        tenant_email = request.form.get('tenant_email', '').strip().lower()
        rent_amount = request.form.get('rent_amount', '').strip()
        rent_frequency = request.form.get('rent_frequency', '')
        rent_due_day_of_week = request.form.get('rent_due_day_of_week')
        rent_due_day = request.form.get('rent_due_day')
        bank_statement_keyword = request.form.get('bank_statement_keyword', '').strip()
        send_tenant_reminder = bool(request.form.get('send_tenant_reminder'))

        # Validation
        if not all([address, tenant_name, tenant_email, rent_amount, rent_frequency, bank_statement_keyword]):
            flash('Please fill in all required fields.', 'error')
            return render_template('properties/add.html')

        try:
            rent_amount = Decimal(rent_amount)
            if rent_amount <= 0:
                raise ValueError("Rent amount must be positive")
        except (ValueError, TypeError):
            flash('Please enter a valid rent amount.', 'error')
            return render_template('properties/add.html')

        # Validate rent frequency and due date
        if rent_frequency not in ['Weekly', 'Fortnightly', 'Monthly']:
            flash('Please select a valid rent frequency.', 'error')
            return render_template('properties/add.html')

        if rent_frequency in ['Weekly', 'Fortnightly']:
            if not rent_due_day_of_week or int(rent_due_day_of_week) not in range(7):
                flash('Please select a valid day of the week.', 'error')
                return render_template('properties/add.html')
            rent_due_day_of_week = int(rent_due_day_of_week)
            rent_due_day = None
        else:  # Monthly
            if not rent_due_day or int(rent_due_day) not in range(1, 32):
                flash('Please select a valid day of the month.', 'error')
                return render_template('properties/add.html')
            rent_due_day = int(rent_due_day)
            rent_due_day_of_week = None

        # Create property
        property = Property(
            user_id=current_user.id,
            address=address,
            tenant_name=tenant_name,
            tenant_email=tenant_email,
            rent_amount=rent_amount,
            rent_frequency=rent_frequency,
            rent_due_day_of_week=rent_due_day_of_week,
            rent_due_day=rent_due_day,
            bank_statement_keyword=bank_statement_keyword,
            send_tenant_reminder=send_tenant_reminder
        )

        db.session.add(property)
        db.session.commit()

        flash('Property added successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('properties/add.html')

@properties_bp.route('/edit/<int:property_id>', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property = Property.query.filter_by(id=property_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        # Get form data
        address = request.form.get('address', '').strip()
        tenant_name = request.form.get('tenant_name', '').strip()
        tenant_email = request.form.get('tenant_email', '').strip().lower()
        rent_amount = request.form.get('rent_amount', '').strip()
        rent_frequency = request.form.get('rent_frequency', '')
        rent_due_day_of_week = request.form.get('rent_due_day_of_week')
        rent_due_day = request.form.get('rent_due_day')
        bank_statement_keyword = request.form.get('bank_statement_keyword', '').strip()
        send_tenant_reminder = bool(request.form.get('send_tenant_reminder'))

        # Validation
        if not all([address, tenant_name, tenant_email, rent_amount, rent_frequency, bank_statement_keyword]):
            flash('Please fill in all required fields.', 'error')
            return render_template('properties/edit.html', property=property)

        try:
            rent_amount = Decimal(rent_amount)
            if rent_amount <= 0:
                raise ValueError("Rent amount must be positive")
        except (ValueError, TypeError):
            flash('Please enter a valid rent amount.', 'error')
            return render_template('properties/edit.html', property=property)

        # Validate rent frequency and due date
        if rent_frequency not in ['Weekly', 'Fortnightly', 'Monthly']:
            flash('Please select a valid rent frequency.', 'error')
            return render_template('properties/edit.html', property=property)

        if rent_frequency in ['Weekly', 'Fortnightly']:
            if not rent_due_day_of_week or int(rent_due_day_of_week) not in range(7):
                flash('Please select a valid day of the week.', 'error')
                return render_template('properties/edit.html', property=property)
            rent_due_day_of_week = int(rent_due_day_of_week)
            rent_due_day = None
        else:  # Monthly
            if not rent_due_day or int(rent_due_day) not in range(1, 32):
                flash('Please select a valid day of the month.', 'error')
                return render_template('properties/edit.html', property=property)
            rent_due_day = int(rent_due_day)
            rent_due_day_of_week = None

        # Update property
        property.address = address
        property.tenant_name = tenant_name
        property.tenant_email = tenant_email
        property.rent_amount = rent_amount
        property.rent_frequency = rent_frequency
        property.rent_due_day_of_week = rent_due_day_of_week
        property.rent_due_day = rent_due_day
        property.bank_statement_keyword = bank_statement_keyword
        property.send_tenant_reminder = send_tenant_reminder

        db.session.commit()

        flash('Property updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('properties/edit.html', property=property)

@properties_bp.route('/delete/<int:property_id>', methods=['POST'])
@login_required
def delete_property(property_id):
    property = Property.query.filter_by(id=property_id, user_id=current_user.id).first_or_404()

    db.session.delete(property)
    db.session.commit()

    flash('Property deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@properties_bp.route('/search_transactions')
@login_required
def search_transactions():
    # This will be implemented when we have the Akahu integration
    # For now, return empty list
    return jsonify({
        'success': True,
        'transactions': []
    })