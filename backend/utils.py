import re
import math
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo('Asia/Kolkata')

def validate_email(email):
    """Check if email is valid"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Check password strength"""
    if len(password) < 6:
        return False, "Password must be 6+ characters"
    if not re.search(r'[A-Z]', password):
        return False, "Need uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Need lowercase letter"
    if not re.search(r'\d', password):
        return False, "Need digit"
    return True, "Valid"

def validate_phone(phone):
    """Check if phone is valid Indian format"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_pincode(pincode):
    """Check if pincode is valid Indian format"""
    pattern = r'^\d{6}$'
    return re.match(pattern, pincode) is not None

def calculate_parking_cost(entry_time, exit_time, price_per_hour):
    """Calculate parking cost - rounds UP to nearest hour"""
    if not exit_time:
        return 0.0
    
    duration = exit_time - entry_time
    hours = duration.total_seconds() / 3600
    hours = math.ceil(hours)  # Round up
    
    cost = hours * price_per_hour
    return round(cost, 2)

def generate_html_report(user_name, reservations):
    """Generate HTML parking report"""
    total_cost = sum(r.Total_Cost or 0 for r in reservations)
    
    rows = ""
    for idx, res in enumerate(reservations, 1):
        entry = res.Entry_Time.strftime('%d-%m-%Y %H:%M') if res.Entry_Time else 'N/A'
        exit_time = res.Exit_Time.strftime('%d-%m-%Y %H:%M') if res.Exit_Time else 'Active'
        duration = "Active" if not res.Exit_Time else f"{(res.Exit_Time - res.Entry_Time).total_seconds() / 3600:.2f}h"
        
        rows += f"""
        <tr>
            <td>{idx}</td>
            <td>{res.allocated_spot.belong_to_lot.Location_Name}</td>
            <td>{res.allocated_spot.Spot_Number}</td>
            <td>{res.Vehicle_Number}</td>
            <td>{entry}</td>
            <td>{exit_time}</td>
            <td>{duration}</td>
            <td>Rs. {res.Total_Cost or 0:.2f}</td>
        </tr>
        """
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .summary {{ padding: 15px; background: #f0f0f0; border-radius: 5px; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #4CAF50; color: white; padding: 10px; text-align: left; }}
            td {{ border: 1px solid #ddd; padding: 10px; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>Parking Activity Report</h1>
        <p><strong>User:</strong> {user_name}</p>
        
        <div class="summary">
            <p><strong>Total Bookings:</strong> {len(reservations)}</p>
            <p><strong>Total Spent:</strong> Rs. {total_cost:.2f}</p>
        </div>
        
        <table>
            <tr>
                <th>#</th>
                <th>Parking Lot</th>
                <th>Spot</th>
                <th>Vehicle</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>Duration</th>
                <th>Cost</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
    return html
