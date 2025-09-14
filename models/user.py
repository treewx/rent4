from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.Text)
    email_verification_expires = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Subscription fields
    is_premium = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    subscription_status = db.Column(db.String(50))

    # Akahu integration
    akahu_app_token = db.Column(db.String(255))
    akahu_user_token = db.Column(db.String(255))

    # Relationships
    properties = db.relationship('Property', backref='landlord', lazy=True)
    settings = db.relationship('UserSetting', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_add_property(self):
        property_count = Property.query.filter_by(user_id=self.id).count()
        return property_count == 0 or self.is_premium

    def get_property_limit(self):
        return 1 if not self.is_premium else float('inf')

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class UserSetting(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    setting_key = db.Column(db.Text, nullable=False)
    setting_value = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint('user_id', 'setting_key'),)