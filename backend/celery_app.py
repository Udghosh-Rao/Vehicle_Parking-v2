from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import io
import csv

from app import create_app
from extensions import db, cache
from models import VehicleUser, ParkingReservation, ParkingLot
from mail import (
    send_daily_reminder_email,
    send_monthly_report_email,
    send_email,   #  add for CSV export email
)

IST = ZoneInfo("Asia/Kolkata")

# 1. Create Flask app and Celery instance
flask_app = create_app()

celery = Celery(
    "vehicle_parking",
    broker="redis://localhost:6379/1",   # Redis DB 1 as broker
    backend="redis://localhost:6379/2",  # Redis DB 2 as result backend
)

celery.conf.timezone = "Asia/Kolkata"

# 2. Beat schedule 
celery.conf.beat_schedule = {
    # Runs every day at 18:00 pm
    "daily-reminder-6pm": {
        "task": "tasks.send_daily_reminder",
        "schedule": crontab(hour=18, minute=0),
    },
    # Runs 1st of every month at 12:05 am
    "monthly-report-1st": {
        "task": "tasks.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=0, minute=5),
    },
    # refresh lot cache every 5 minutes
    "cache-parking-lots": {
        "task": "tasks.cache_parking_lots",
        "schedule": crontab(minute="*/5"),
    },
}


# 3. build monthly HTML report 
def build_monthly_report_html(user, reservations):
    total_bookings = len(reservations)
    total_spent = sum(r.Total_Cost or 0 for r in reservations)

    # most used lot
    lot_count = {}
    for r in reservations:
        lot_name = (
            r.allocated_spot.belong_to_lot.Location_Name
            if r.allocated_spot else "Unknown"
        )
        lot_count[lot_name] = lot_count.get(lot_name, 0) + 1

    most_used_lot = max(lot_count, key=lot_count.get) if lot_count else "N/A"

    rows_html = ""
    for r in reservations:
        lot_name = (
            r.allocated_spot.belong_to_lot.Location_Name
            if r.allocated_spot else "Unknown"
        )
        spot = r.allocated_spot.Spot_Number if r.allocated_spot else "-"
        entry = r.Entry_Time.strftime("%d-%m-%Y %H:%M") if r.Entry_Time else "-"
        exit_ = r.Exit_Time.strftime("%d-%m-%Y %H:%M") if r.Exit_Time else "-"
        cost = r.Total_Cost if r.Total_Cost is not None else 0

        rows_html += f"""
        <tr>
            <td>{lot_name}</td>
            <td>{spot}</td>
            <td>{r.Vehicle_Number}</td>
            <td>{entry}</td>
            <td>{exit_}</td>
            <td>₹ {cost:.2f}</td>
        </tr>
        """

    html = f"""
    <div style="font-family:Arial, sans-serif;">
        <h2 style="margin-bottom:8px;">Monthly Summary</h2>
        <p><strong>Total Bookings:</strong> {total_bookings}</p>
        <p><strong>Total Spent:</strong> ₹ {total_spent:.2f}</p>
        <p><strong>Most Used Lot:</strong> {most_used_lot}</p>

        <h3 style="margin-top:24px;">Booking Details</h3>
        <table border="1" cellpadding="6" cellspacing="0"
               style="border-collapse:collapse; font-size:13px;">
            <thead style="background:#f3f4f6;">
                <tr>
                    <th>Lot</th>
                    <th>Spot</th>
                    <th>Vehicle</th>
                    <th>Entry</th>
                    <th>Exit</th>
                    <th>Cost</th>
                </tr>
            </thead>
            <tbody>
                {rows_html or "<tr><td colspan='6'>No bookings this month.</td></tr>"}
            </tbody>
        </table>
    </div>
    """
    return html


# 4. Celery tasks

@celery.task(name="tasks.send_daily_reminder")
def send_daily_reminder():
    """Send daily reminder emails to all regular users."""
    with flask_app.app_context():
        users = VehicleUser.query.filter_by(Role="user").all()
        for user in users:
            # If you want a condition like "has not visited recently", add it here
            send_daily_reminder_email(user.Email_Address, user.Full_Name)
        print(f" Daily reminder sent to {len(users)} users")


@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    """Generate monthly report for each user and send via email."""
    with flask_app.app_context():
        today = datetime.now(IST)
        # First day of this month
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # First day of next month
        next_month = (start + timedelta(days=32)).replace(day=1)

        users = VehicleUser.query.filter_by(Role="user").all()
        for user in users:
            reservations = (
                ParkingReservation.query
                .filter(
                    ParkingReservation.User_id == user.User_id,
                    ParkingReservation.Entry_Time >= start,
                    ParkingReservation.Entry_Time < next_month,
                )
                .order_by(ParkingReservation.Entry_Time.asc())
                .all()
            )

            report_html = build_monthly_report_html(user, reservations)
            send_monthly_report_email(
                user.Email_Address,
                user.Full_Name,
                report_html
            )

        print(f" Monthly reports generated for {len(users)} users")


@celery.task(name="tasks.cache_parking_lots")
def cache_parking_lots():
    """Periodically cache parking lots list in Redis to speed up API."""
    with flask_app.app_context():
        lots = ParkingLot.query.all()
        data = [lot.to_dict() for lot in lots]
        cache.set("parking_lots_cached", data, timeout=300)  # 5 minutes
        print(f" Cached {len(lots)} parking lots")


@celery.task(name="tasks.export_user_history")
def export_user_history(user_id):
    """
    Async job: export user parking history as CSV and
    send it to the user via email. Also store CSV in Redis.
    """
    with flask_app.app_context():
        # 1) Get user
        user = VehicleUser.query.get(user_id)
        if not user:
            print(f"[EXPORT] No user found for id={user_id}")
            return None

        # 2) Get all reservations for this user
        reservations = (
            ParkingReservation.query
            .filter_by(User_id=user_id)
            .order_by(ParkingReservation.Entry_Time.desc())
            .all()
        )

        # 3) Build CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Reservation_ID",
            "Lot",
            "Spot",
            "Vehicle",
            "Entry_Time",
            "Exit_Time",
            "Duration_Hours",
            "Total_Cost",
            "Notes",
        ])

        for r in reservations:
            lot_name = (
                r.allocated_spot.belong_to_lot.Location_Name
                if r.allocated_spot else "Unknown"
            )
            spot = r.allocated_spot.Spot_Number if r.allocated_spot else "-"
            duration = None
            if r.Entry_Time and r.Exit_Time:
                duration = round(
                    (r.Exit_Time - r.Entry_Time).total_seconds() / 3600, 2
                )

            writer.writerow([
                r.Reservation_Id,
                lot_name,
                spot,
                r.Vehicle_Number,
                r.Entry_Time.isoformat() if r.Entry_Time else "",
                r.Exit_Time.isoformat() if r.Exit_Time else "",
                duration if duration is not None else "",
                r.Total_Cost if r.Total_Cost is not None else "",
                r.Notes or "",
            ])

        csv_data = output.getvalue()
        output.close()

        # 4) Store CSV string in Redis for 1 hour (optional)
        cache_key = f"export_user_{user_id}"
        cache.set(cache_key, csv_data, timeout=3600)

        # 5) Send email to user with CSV content (for demo we embed it)
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Your Parking CSV Export is Ready</h2>
            <p>Hello {user.Full_Name},</p>
            <p>We have generated your parking history CSV. For this demo,
            the CSV content is included below:</p>
            <pre style="background:#f3f4f6; padding:12px; border-radius:4px;
                        font-size:12px; white-space:pre-wrap;">
{csv_data}
            </pre>
            <p><em>In a real deployment, this CSV could be attached as a file
            or provided as a download link.</em></p>
            <p> Vehicle Parking App</p>
        </body>
        </html>
        """

        send_email(
            user.Email_Address,
            "parking CSV export is ready",
            body,
            is_html=True
        )

        print(
            f"✓ Exported history for user_id={user_id}, "
            f"{len(reservations)} rows and emailed CSV"
        )
        return cache_key
