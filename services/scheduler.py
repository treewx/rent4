import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask
import logging

logger = logging.getLogger(__name__)

def init_scheduler(app: Flask):
    """Initialize the payment checking scheduler"""
    if os.environ.get('FLASK_ENV') == 'development':
        logger.info("Development mode: Scheduler disabled")
        return

    scheduler = BackgroundScheduler()

    # Schedule rent payment checking to run every morning at 8:00 AM
    scheduler.add_job(
        func=check_payments_job,
        trigger=CronTrigger(hour=8, minute=0),
        id='check_rent_payments',
        name='Check rent payments daily',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Payment checking scheduler started")

    # Shutdown scheduler when app context ends
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        if scheduler.running:
            scheduler.shutdown()

def check_payments_job():
    """Job function to check rent payments"""
    from routes.payments import check_rent_payments
    from app import create_app

    app = create_app()
    with app.app_context():
        try:
            check_rent_payments()
            logger.info("Daily rent payment check completed")
        except Exception as e:
            logger.error(f"Error in daily rent payment check: {str(e)}")