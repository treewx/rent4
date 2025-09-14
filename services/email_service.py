import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.environ.get('GMAIL_USER')
        self.sender_password = os.environ.get('GMAIL_APP_PASSWORD')

    def send_email(self, recipient_email, subject, html_body, text_body=None):
        try:
            if not self.sender_email or not self.sender_password:
                logger.warning("Email credentials not configured. Skipping email send.")
                if current_app.config.get('TESTING') or os.environ.get('FLASK_ENV') == 'development':
                    logger.info(f"DEV MODE: Would send email to {recipient_email}")
                    logger.info(f"Subject: {subject}")
                    logger.info(f"Body: {html_body}")
                    return True
                return False

            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    def send_email_verification(self, recipient_email, first_name, verification_url):
        subject = "Verify Your Email Address - Rent4"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">Welcome to Rent4!</h1>

                <p>Hello {first_name},</p>

                <p>Thank you for signing up for Rent4. To complete your registration and start managing your rental properties, please verify your email address.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>

                <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{verification_url}</p>

                <p>This verification link will expire in 24 hours.</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    If you didn't create an account with us, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Rent4!

        Hello {first_name},

        Thank you for signing up for Rent4. To complete your registration, please verify your email address by visiting:

        {verification_url}

        This verification link will expire in 24 hours.

        If you didn't create an account with us, please ignore this email.
        """

        return self.send_email(recipient_email, subject, html_body, text_body)

    def send_password_reset_email(self, recipient_email, first_name, reset_url):
        subject = "Reset Your Password - Rent4"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">Password Reset Request</h1>

                <p>Hello {first_name},</p>

                <p>We received a request to reset your password for your Rent4 account. If you made this request, click the button below to reset your password:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Reset Password
                    </a>
                </div>

                <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>

                <p>This password reset link will expire in 24 hours.</p>

                <p><strong>If you didn't request a password reset, please ignore this email.</strong> Your password will not be changed unless you click the link above.</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    This is an automated email from Rent4. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(recipient_email, subject, html_body)

    def send_notification_email(self, recipient_email, subject, message):
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">Rent4 Notification</h1>

                <div style="background: white; padding: 20px; border-radius: 5px; border-left: 4px solid #007bff;">
                    {message}
                </div>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    This is an automated notification from Rent4.
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(recipient_email, subject, html_body)

    def send_rent_received_notification(self, landlord_email, property_address, tenant_name, amount, date):
        subject = f"Rent Received - {property_address}"
        message = f"""
        <h2 style="color: #28a745;">✓ Rent Payment Received</h2>
        <p><strong>Property:</strong> {property_address}</p>
        <p><strong>Tenant:</strong> {tenant_name}</p>
        <p><strong>Amount:</strong> ${amount}</p>
        <p><strong>Date:</strong> {date}</p>
        <p>The rent payment has been successfully received and processed.</p>
        """
        return self.send_notification_email(landlord_email, subject, message)

    def send_rent_missed_notification(self, landlord_email, property_address, tenant_name, amount, due_date):
        subject = f"Rent Payment Missed - {property_address}"
        message = f"""
        <h2 style="color: #dc3545;">⚠ Rent Payment Missed</h2>
        <p><strong>Property:</strong> {property_address}</p>
        <p><strong>Tenant:</strong> {tenant_name}</p>
        <p><strong>Expected Amount:</strong> ${amount}</p>
        <p><strong>Due Date:</strong> {due_date}</p>
        <p>No matching rent payment was found in your bank statements. You may want to follow up with your tenant.</p>
        """
        return self.send_notification_email(landlord_email, subject, message)

    def send_rent_partial_notification(self, landlord_email, property_address, tenant_name, expected_amount, actual_amount, date):
        subject = f"Partial Rent Payment - {property_address}"
        message = f"""
        <h2 style="color: #ffc107;">⚠ Partial Rent Payment Received</h2>
        <p><strong>Property:</strong> {property_address}</p>
        <p><strong>Tenant:</strong> {tenant_name}</p>
        <p><strong>Expected Amount:</strong> ${expected_amount}</p>
        <p><strong>Amount Received:</strong> ${actual_amount}</p>
        <p><strong>Date:</strong> {date}</p>
        <p>A payment was received but the amount differs from the expected rent. Please review and follow up as needed.</p>
        """
        return self.send_notification_email(landlord_email, subject, message)

    def send_tenant_reminder(self, tenant_email, tenant_name, property_address, amount, due_date):
        subject = "Rent Payment Reminder"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rent Payment Reminder</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">Rent Payment Reminder</h1>

                <p>Dear {tenant_name},</p>

                <p>This is a friendly reminder that your rent payment was due and we haven't received it yet.</p>

                <div style="background: white; padding: 20px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p><strong>Property:</strong> {property_address}</p>
                    <p><strong>Amount Due:</strong> ${amount}</p>
                    <p><strong>Due Date:</strong> {due_date}</p>
                </div>

                <p>Please ensure your rent payment is processed as soon as possible. If you have already made the payment, please disregard this message.</p>

                <p>If you have any questions or need to discuss your payment, please contact your landlord directly.</p>

                <p>Thank you for your prompt attention to this matter.</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    This is an automated reminder from your landlord's property management system.
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(tenant_email, subject, html_body)