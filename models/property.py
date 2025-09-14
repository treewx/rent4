from app import db
from datetime import datetime, timezone

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Property details
    address = db.Column(db.Text, nullable=False)
    tenant_name = db.Column(db.String(255), nullable=False)
    tenant_email = db.Column(db.String(255), nullable=False)

    # Rent details
    rent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    rent_frequency = db.Column(db.String(20), nullable=False)  # Weekly, Fortnightly, Monthly
    rent_due_day_of_week = db.Column(db.Integer)  # 0=Monday, 6=Sunday (for Weekly/Fortnightly)
    rent_due_day = db.Column(db.Integer)  # 1-31 (for Monthly)

    # Bank statement identification
    bank_statement_keyword = db.Column(db.String(255), nullable=False)

    # Email settings
    send_tenant_reminder = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Property {self.address}>'

class RentPayment(db.Model):
    __tablename__ = 'rent_payments'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)

    # Payment details
    expected_amount = db.Column(db.Numeric(10, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(10, 2))
    due_date = db.Column(db.Date, nullable=False)
    received_date = db.Column(db.Date)

    # Status
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'received', 'missed', 'partial'

    # Bank transaction details
    transaction_description = db.Column(db.Text)
    transaction_reference = db.Column(db.String(255))

    # Email notifications
    landlord_notified = db.Column(db.Boolean, default=False)
    tenant_notified = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    property = db.relationship('Property', backref='rent_payments')

    def __repr__(self):
        return f'<RentPayment {self.property_id} - {self.due_date}>'