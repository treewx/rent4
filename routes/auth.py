import os
import secrets
from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash

from app import db
from flask import current_app
from models.user import User, PasswordResetToken
from services.email_service import EmailService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
email_service = EmailService()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        # Validation
        if not email or not password or not first_name or not last_name:
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')

        # Email validation
        try:
            validated_email = validate_email(email)
            email = validated_email.email
        except EmailNotValidError as e:
            flash('Please enter a valid email address.', 'error')
            return render_template('auth/register.html')

        # Password validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return render_template('auth/register.html')

        # Create user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)

        # Generate email verification token
        user.email_verification_token = secrets.token_urlsafe(32)
        user.email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)

        db.session.add(user)
        db.session.commit()

        # Send verification email in background to prevent blocking
        verification_url = url_for('auth.verify_email',
                                   token=user.email_verification_token,
                                   _external=True)

        # Try to send email but don't block the response
        try:
            from threading import Thread
            def send_email_async():
                try:
                    email_service.send_email_verification(email, first_name, verification_url)
                except Exception as e:
                    current_app.logger.error(f"Failed to send verification email: {e}")

            Thread(target=send_email_async, daemon=True).start()
            flash('Registration successful! Please check your email to verify your account.', 'success')
        except Exception as e:
            current_app.logger.error(f"Failed to start email thread: {e}")
            flash('Registration successful! However, we couldn\'t send the verification email. Please try to resend it.', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')

        if not user.email_verified:
            flash('Please verify your email address before logging in.', 'error')
            return render_template('auth/login.html')

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        login_user(user, remember=remember_me)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)

        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()

    if not user:
        flash('Invalid or expired verification token.', 'error')
        return redirect(url_for('auth.login'))

    if user.email_verification_expires < datetime.now(timezone.utc):
        flash('Verification token has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.resend_verification'))

    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    db.session.commit()

    flash('Email verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('auth/resend_verification.html')

        user = User.query.filter_by(email=email).first()

        if user and not user.email_verified:
            # Generate new token
            user.email_verification_token = secrets.token_urlsafe(32)
            user.email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
            db.session.commit()

            # Send verification email
            verification_url = url_for('auth.verify_email',
                                       token=user.email_verification_token,
                                       _external=True)

            email_service.send_email_verification(email, user.first_name, verification_url)

        # Always show the same message to prevent email enumeration
        flash('If an account with that email exists and is unverified, we\'ve sent a new verification email.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/resend_verification.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('auth/forgot_password.html')

        user = User.query.filter_by(email=email).first()

        if user:
            # Clean up old tokens
            PasswordResetToken.query.filter_by(user_id=user.id).delete()

            # Create new reset token
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=secrets.token_urlsafe(32),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            db.session.add(reset_token)
            db.session.commit()

            # Send reset email
            reset_url = url_for('auth.reset_password',
                                token=reset_token.token,
                                _external=True)

            email_service.send_password_reset_email(email, user.first_name, reset_url)

        # Always show the same message to prevent email enumeration
        flash('If an account with that email exists, we\'ve sent you a password reset link.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()

    if not reset_token or reset_token.expires_at < datetime.now(timezone.utc):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password:
            flash('Please enter a password.', 'error')
            return render_template('auth/reset_password.html', token=token)

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', token=token)

        # Update user password
        user = User.query.get(reset_token.user_id)
        user.set_password(password)

        # Mark token as used
        reset_token.used = True

        db.session.commit()

        flash('Password reset successful! You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)