import requests
import os
from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from decimal import Decimal

from models.property import Property, RentPayment
from services.email_service import EmailService
from app import db

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')
email_service = EmailService()

@payments_bp.route('/check')
@login_required
def check_payments():
    """Manual trigger for checking payments (for testing)"""
    check_rent_payments()
    return jsonify({'success': True, 'message': 'Payment check completed'})

def check_rent_payments():
    """Check for rent payments for the previous day"""
    yesterday = date.today() - timedelta(days=1)

    # Get all properties for all users
    properties = Property.query.all()

    for property in properties:
        if is_rent_due(property, yesterday):
            process_rent_payment(property, yesterday)

def is_rent_due(property, check_date):
    """Check if rent is due on the given date for this property"""
    if property.rent_frequency == 'Weekly':
        return check_date.weekday() == property.rent_due_day_of_week
    elif property.rent_frequency == 'Fortnightly':
        # For simplicity, we'll check if it's the right day of week
        # In a real system, you'd track the actual fortnightly cycle
        return check_date.weekday() == property.rent_due_day_of_week
    elif property.rent_frequency == 'Monthly':
        return check_date.day == property.rent_due_day

    return False

def process_rent_payment(property, check_date):
    """Process rent payment checking for a property"""
    landlord = property.landlord

    # Check if we already processed this date
    existing_payment = RentPayment.query.filter_by(
        property_id=property.id,
        due_date=check_date
    ).first()

    if existing_payment:
        return  # Already processed

    # Check bank transactions
    transaction = get_bank_transaction(landlord, property, check_date)

    if transaction is None:
        # No matching transaction found - rent missed
        rent_payment = RentPayment(
            property_id=property.id,
            expected_amount=property.rent_amount,
            due_date=check_date,
            status='missed'
        )
        db.session.add(rent_payment)
        db.session.commit()

        # Send notification to landlord
        email_service.send_rent_missed_notification(
            landlord.email,
            property.address,
            property.tenant_name,
            property.rent_amount,
            check_date.strftime('%Y-%m-%d')
        )

        # Send reminder to tenant if enabled
        if property.send_tenant_reminder:
            email_service.send_tenant_reminder(
                property.tenant_email,
                property.tenant_name,
                property.address,
                property.rent_amount,
                check_date.strftime('%Y-%m-%d')
            )

    else:
        # Transaction found - check amount
        transaction_amount = Decimal(str(transaction['amount']))
        expected_amount = property.rent_amount

        if transaction_amount == expected_amount:
            # Exact match - rent received
            rent_payment = RentPayment(
                property_id=property.id,
                expected_amount=expected_amount,
                actual_amount=transaction_amount,
                due_date=check_date,
                received_date=datetime.strptime(transaction['date'], '%Y-%m-%d').date(),
                status='received',
                transaction_description=transaction['description']
            )
            db.session.add(rent_payment)
            db.session.commit()

            email_service.send_rent_received_notification(
                landlord.email,
                property.address,
                property.tenant_name,
                transaction_amount,
                transaction['date']
            )

        else:
            # Amount mismatch - partial payment
            rent_payment = RentPayment(
                property_id=property.id,
                expected_amount=expected_amount,
                actual_amount=transaction_amount,
                due_date=check_date,
                received_date=datetime.strptime(transaction['date'], '%Y-%m-%d').date(),
                status='partial',
                transaction_description=transaction['description']
            )
            db.session.add(rent_payment)
            db.session.commit()

            email_service.send_rent_partial_notification(
                landlord.email,
                property.address,
                property.tenant_name,
                expected_amount,
                transaction_amount,
                transaction['date']
            )

def get_bank_transaction(landlord, property, check_date):
    """Get bank transaction from Akahu API"""
    if not landlord.akahu_app_token or not landlord.akahu_user_token:
        return None

    try:
        # Mock implementation - replace with actual Akahu API call
        # This is a simplified version for demonstration
        headers = {
            'Authorization': f'Bearer {landlord.akahu_user_token}',
            'X-Akahu-ID': landlord.akahu_app_token
        }

        # Format date for API
        date_str = check_date.strftime('%Y-%m-%d')

        # In a real implementation, you would call the Akahu API here
        # For now, we'll return None to simulate no transaction found
        #
        # Example API call (commented out):
        # response = requests.get(
        #     f'https://api.akahu.nz/v1/transactions',
        #     headers=headers,
        #     params={
        #         'start': date_str,
        #         'end': date_str
        #     }
        # )
        #
        # if response.status_code == 200:
        #     transactions = response.json().get('items', [])
        #     for transaction in transactions:
        #         if property.bank_statement_keyword.lower() in transaction['description'].lower():
        #             return transaction

        return None

    except Exception as e:
        print(f"Error fetching bank transactions: {e}")
        return None

@payments_bp.route('/history/<int:property_id>')
@login_required
def payment_history(property_id):
    """View payment history for a property"""
    property = Property.query.filter_by(id=property_id, user_id=current_user.id).first_or_404()
    payments = RentPayment.query.filter_by(property_id=property_id).order_by(RentPayment.due_date.desc()).all()

    return render_template('payments/history.html', property=property, payments=payments)