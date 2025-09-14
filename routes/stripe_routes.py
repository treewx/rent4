import os
import stripe
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from models.user import User

stripe_bp = Blueprint('stripe_routes', __name__, url_prefix='/subscription')

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

@stripe_bp.route('/upgrade')
@login_required
def upgrade():
    """Show upgrade page"""
    if current_user.is_premium:
        flash('You already have a premium account!', 'info')
        return redirect(url_for('main.dashboard'))

    return render_template('stripe/upgrade.html',
                           stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@stripe_bp.route('/create_checkout_session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=f"{current_user.first_name} {current_user.last_name}",
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
        else:
            customer = stripe.Customer.retrieve(current_user.stripe_customer_id)

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'nzd',
                    'product_data': {
                        'name': 'Rent4 Premium Subscription',
                        'description': 'Unlimited property management'
                    },
                    'unit_amount': 1000,  # $10.00 NZD in cents
                    'recurring': {
                        'interval': 'month',
                        'interval_count': 1,
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('stripe_routes.success', _external=True),
            cancel_url=url_for('stripe_routes.upgrade', _external=True),
            metadata={'user_id': current_user.id}
        )

        return jsonify({'checkout_url': checkout_session.url})

    except Exception as e:
        current_app.logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

@stripe_bp.route('/success')
@login_required
def success():
    """Handle successful subscription"""
    flash('Welcome to Rent4 Premium! You can now add unlimited properties.', 'success')
    return redirect(url_for('main.dashboard'))

@stripe_bp.route('/cancel')
@login_required
def cancel():
    """Handle cancelled subscription"""
    flash('Subscription cancelled. You can try again anytime.', 'info')
    return redirect(url_for('main.dashboard'))

@stripe_bp.route('/manage')
@login_required
def manage_subscription():
    """Manage existing subscription"""
    if not current_user.is_premium or not current_user.stripe_customer_id:
        flash('You don\'t have an active subscription to manage.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        # Create customer portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for('main.dashboard', _external=True)
        )
        return redirect(portal_session.url)

    except Exception as e:
        current_app.logger.error(f"Error creating portal session: {str(e)}")
        flash('Unable to access subscription management at this time.', 'error')
        return redirect(url_for('main.dashboard'))

@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        current_app.logger.error("Invalid payload in Stripe webhook")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        current_app.logger.error("Invalid signature in Stripe webhook")
        return 'Invalid signature', 400

    # Handle different event types
    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_payment_failed(event['data']['object'])

    return 'Success', 200

def handle_subscription_created(subscription):
    """Handle subscription creation"""
    try:
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        status = subscription['status']

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.stripe_subscription_id = subscription_id
            user.subscription_status = status
            user.is_premium = (status == 'active')
            db.session.commit()
            current_app.logger.info(f"Subscription created for user {user.id}")

    except Exception as e:
        current_app.logger.error(f"Error handling subscription created: {str(e)}")

def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    try:
        customer_id = subscription['customer']
        status = subscription['status']

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_status = status
            user.is_premium = (status == 'active')
            db.session.commit()
            current_app.logger.info(f"Subscription updated for user {user.id}: {status}")

    except Exception as e:
        current_app.logger.error(f"Error handling subscription updated: {str(e)}")

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription['customer']

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_status = 'canceled'
            user.is_premium = False
            db.session.commit()
            current_app.logger.info(f"Subscription canceled for user {user.id}")

    except Exception as e:
        current_app.logger.error(f"Error handling subscription deleted: {str(e)}")

def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    try:
        customer_id = invoice['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            current_app.logger.info(f"Payment succeeded for user {user.id}")

    except Exception as e:
        current_app.logger.error(f"Error handling payment succeeded: {str(e)}")

def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        customer_id = invoice['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            current_app.logger.warning(f"Payment failed for user {user.id}")

    except Exception as e:
        current_app.logger.error(f"Error handling payment failed: {str(e)}")