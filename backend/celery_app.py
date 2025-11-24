from celery import Celery
from datetime import datetime
from zoneinfo import ZoneInfo
import csv
import io

# Absolute imports with your package name 'backend'
from backend.extensions import db, cache
from backend.models import VehicleUser, ParkingReservation, ParkingLot
from backend.utils import generate_html_report
from backend.app import create_app

IST = ZoneInfo('Asia/Kolkata')

# Initialize Celery instance
celeryApp = Celery('backend')
celeryApp.conf.broker_url = 'redis://localhost:6379/1'
celeryApp.conf.result_backend = 'redis://localhost:6379/2'

from celery.schedules import crontab

celeryApp.conf.beat_schedule = {
    'cache-lots-every-5-min': {
        'task': 'backend.celery_app.cache_parking_lots',
        'schedule': 300.0,
    },
    'daily-reminder-6pm': {
        'task': 'backend.celery_app.send_daily_reminder',
        'schedule': crontab(hour=18, minute=0),
    },
    'monthly-report-1st': {
        'task': 'backend.celery_app.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
}

@celeryApp.task
def cache_parking_lots():
    app = create_app()
    with app.app_context():
        lots = ParkingLot.query.all()
        lots_data = [lot.to_dict() for lot in lots]
        cache.set('parking_lots', lots_data, timeout=300)
        print(f"[CACHE] Parking lots cached: {len(lots)} lots")
    return f'Cached {len(lots)} lots'


@celeryApp.task
def send_daily_reminder():
    app = create_app()
    with app.app_context():
        users = VehicleUser.query.filter_by(Role='user').all()
        for user in users:
            print(f"[REMINDER] Dear {user.Full_Name}, Book a parking spot today!")
            # TODO: import and call send_daily_reminder_email(user.Email_Address, user.Full_Name)
        return f'Reminders sent to {len(users)} users'


@celeryApp.task
def generate_monthly_report():
    app = create_app()
    with app.app_context():
        users = VehicleUser.query.filter_by(Role='user').all()
        for user in users:
            today = datetime.now(IST)
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            reservations = ParkingReservation.query.filter(
                ParkingReservation.User_id == user.User_id,
                ParkingReservation.Entry_Time >= month_start
            ).all()
            if reservations:
                html_report = generate_html_report(user.Full_Name, reservations)
                cache.set(f'report_{user.User_id}', html_report, timeout=2592000)
                print(f"[REPORT] Generated for {user.Full_Name}: {len(reservations)} bookings")
                # TODO: import and call send_monthly_report_email(user.Email_Address, user.Full_Name, html_report)
        return f'Monthly reports generated'


@celeryApp.task
def export_user_history(user_id):
    app = create_app()
    with app.app_context():
        user = VehicleUser.query.get(user_id)
        reservations = ParkingReservation.query.filter_by(User_id=user_id).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Reservation ID', 'Lot', 'Spot', 'Vehicle', 'Entry', 'Exit', 'Duration (hrs)', 'Cost'])

        for res in reservations:
            duration = None
            if res.Entry_Time and res.Exit_Time:
                duration = round((res.Exit_Time - res.Entry_Time).total_seconds() / 3600, 2)
            lot_name = res.allocated_spot.belong_to_lot.Location_Name if res.allocated_spot else 'N/A'
            spot_num = res.allocated_spot.Spot_Number if res.allocated_spot else 'N/A'

            writer.writerow([
                res.Reservation_Id,
                lot_name,
                spot_num,
                res.Vehicle_Number,
                res.Entry_Time.isoformat() if res.Entry_Time else '',
                res.Exit_Time.isoformat() if res.Exit_Time else '',
                duration or '',
                res.Total_Cost or ''
            ])

        csv_data = output.getvalue()
        cache.set(f'export_{user_id}', csv_data, timeout=3600)

        print(f"[EXPORT] CSV created for user {user_id}")
        return f'Export completed'
