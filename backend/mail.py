import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#  SMTP CONFIG FOR MAILHOG
# MailHog SMTP runs on localhost:1025
SMTP_HOST = "127.0.0.1"   
SMTP_PORT = 1025
FROM_EMAIL = "udghosh@gmail.com"


def send_email(to_email, subject, body, is_html=True):
    """Send email using local MailHog SMTP"""
    print(f"\n[DEBUG] Preparing email to {to_email}")
    print(f"[DEBUG] Connecting to SMTP {SMTP_HOST}:{SMTP_PORT} ...")

    try:
        # Create MIME message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email

        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type))

        # Connect to MailHog SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            # show SMTP conversation in this terminal
            server.set_debuglevel(1)
            server.send_message(msg)

        print(f" Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"✗ Failed to send email to {to_email}: {e!r}")
        return False


def send_daily_reminder_email(user_email, user_name):
    subject = " Daily Parking Reminder"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f6f9fc; margin:0; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
            <div style="background:#4a90e2; color:#fff; padding:20px 24px;">
                <h1 style="margin:0;"> Daily Parking Reminder</h1>
            </div>
            <div style="padding:24px; color:#333; font-size:15px; line-height:1.6;">
                <p>Hello {user_name},</p>
                <p>Don't forget to book your parking spot for today! Reserve a spot now to ensure you have a guaranteed space.</p>
                <div style="text-align:center; margin:20px 0;">
                    <a href="http://localhost:5173/user" style="background:#4a90e2; color:#fff; padding:12px 24px; text-decoration:none; border-radius:6px;">Book Now</a>
                </div>
                <p style="color:#666; font-size:13px;">Available parking lots near you:
                    <ul>
                        <li>Mall Parking - Rs. 50/hr</li>
                        <li>Delhi CP - Rs. 50/hr</li>
                    </ul>
                </p>
            </div>
            <div style="background:#f2f6fb; color:#6b7280; padding:12px 24px; font-size:12px;">
                Sent by Vehicle Parking App &middot; admin@parking.com
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(user_email, subject, body, is_html=True)


def send_monthly_report_email(user_email, user_name, report_html):
    subject = f" Monthly Parking Report - {user_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f6f9fc; margin:0; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
            <div style="background:#10b981; color:#fff; padding:20px 24px;">
                <h1 style="margin:0;"> Your Monthly Parking Report</h1>
            </div>
            <div style="padding:24px; color:#333; font-size:15px; line-height:1.6;">
                <p>Hello {user_name},</p>
                <p>Here's your parking activity summary for this month:</p>
                {report_html}
                <p style="margin-top:20px; color:#666; font-size:13px;">
                    Keep parking smart! For any questions, contact admin@parking.com
                </p>
            </div>
            <div style="background:#f2f6fb; color:#6b7280; padding:12px 24px; font-size:12px;">
                Sent by Vehicle Parking App &middot; admin@parking.com
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(user_email, subject, body, is_html=True)


def send_booking_confirmation_email(user_email, user_name, lot_name, spot_number, vehicle):
    subject = " Parking Spot Booked Successfully"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f6f9fc; margin:0; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
            <div style="background:#10b981; color:#fff; padding:20px 24px;">
                <h1 style="margin:0;"> Booking Confirmed</h1>
            </div>
            <div style="padding:24px; color:#333; font-size:15px; line-height:1.6;">
                <p>Hello {user_name},</p>
                <p>Your parking spot has been successfully booked!</p>
                <div style="background:#f0fdf4; border-left:4px solid #10b981; padding:16px; margin:20px 0; border-radius:4px;">
                    <p><strong>Parking Lot:</strong> {lot_name}</p>
                    <p><strong>Spot Number:</strong> {spot_number}</p>
                    <p><strong>Vehicle:</strong> {vehicle}</p>
                </div>
                <p>You can release your spot anytime from your dashboard.</p>
            </div>
            <div style="background:#f2f6fb; color:#6b7280; padding:12px 24px; font-size:12px;">
                Sent by Vehicle Parking App &middot; admin@parking.com
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(user_email, subject, body, is_html=True)


# Simple manual test: python mail.py
if __name__ == "__main__":
    print("Testing email functionality...")

    print("\n1. Testing daily reminder email...")
    send_daily_reminder_email("test@example.com", "John Doe")

    print("\n2. Testing booking confirmation email...")
    send_booking_confirmation_email(
        "test@example.com", "John Doe", "Mall Parking", "A-05", "DL01AB1234"
    )

    print("\n3. Testing monthly report email...")
    report_html = """
    <div style="background:#f3f4f6; padding:16px; border-radius:6px;">
        <p><strong>Total Bookings:</strong> 12</p>
        <p><strong>Total Spent:</strong> Rs. 600</p>
        <p><strong>Most Used Lot:</strong> Mall Parking</p>
    </div>
    """
    send_monthly_report_email("test@example.com", "John Doe", report_html)

    print("\n All test emails attempted!")
