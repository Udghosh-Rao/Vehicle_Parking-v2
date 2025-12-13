from extensions import db
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo('Asia/Kolkata')

class VehicleUser(db.Model):
    __tablename__ = "VehicleUser"
    
    User_id = db.Column(db.Integer, primary_key=True)
    Login_name = db.Column(db.String(100), unique=True, nullable=False)
    Full_Name = db.Column(db.String(150), nullable=False)
    Email_Address = db.Column(db.String(120), unique=True, nullable=False)
    User_Password = db.Column(db.String(255), nullable=False)
    Phone_Number = db.Column(db.String(15), nullable=False)
    Role = db.Column(db.String(20), default="user", nullable=False)  
    Address = db.Column(db.String(300), nullable=False)
    Pin_Code = db.Column(db.String(10), nullable=False)
    Created_At = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    user_reservations = db.relationship("ParkingReservation", backref='customer_booking', cascade="all, delete")
    
    def to_dict(self):
        return {
            "User_id": self.User_id,
            "Login_name": self.Login_name,
            "Full_Name": self.Full_Name,
            "Email_Address": self.Email_Address,
            "Phone_Number": self.Phone_Number,
            "Role": self.Role,
            "Address": self.Address,
            "Pin_Code": self.Pin_Code,
            "Created_At": self.Created_At.isoformat() if self.Created_At else None
        }


class ParkingLot(db.Model):
    __tablename__ = "ParkingLot"
    
    id = db.Column(db.Integer, primary_key=True)
    Location_Name = db.Column(db.String(150), nullable=False)
    Address_name = db.Column(db.String(300), nullable=False)
    PRICE = db.Column(db.Float, nullable=False)
    Maximum_Number_Spots = db.Column(db.Integer, nullable=False)
    Created_At = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    available_spots = db.relationship("ParkingSpot", backref="belong_to_lot", cascade="all, delete", lazy='joined')
    
    def to_dict(self):
        total = len(self.available_spots)
        available = sum(1 for s in self.available_spots if s.Current_Status == 'A')
        occupied = sum(1 for s in self.available_spots if s.Current_Status == 'O')
        
        return {
            "id": self.id,
            "Location_Name": self.Location_Name,
            "Address_name": self.Address_name,
            "PRICE": self.PRICE,
            "Maximum_Number_Spots": self.Maximum_Number_Spots,
            "Available_Spots": available,
            "Occupied_Spots": occupied,
            "Total_Spots": total,
            "Created_At": self.Created_At.isoformat() if self.Created_At else None
        }



class ParkingSpot(db.Model):
    __tablename__ = "ParkingSpot"
    
    Spot_Id = db.Column(db.Integer, primary_key=True)
    Current_Status = db.Column(db.String(1), default='A', nullable=False)  # 'A'=Available, 'O'=Occupied
    Lot_Id = db.Column(db.Integer, db.ForeignKey("ParkingLot.id"), nullable=False)
    Spot_Number = db.Column(db.String(20), nullable=False)
    Created_At = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    spot_reservations = db.relationship("ParkingReservation", backref="allocated_spot", cascade="all, delete")
    
    def to_dict(self):
        return {
            "Spot_Id": self.Spot_Id,
            "Lot_Id": self.Lot_Id,
            "Spot_Number": self.Spot_Number,
            "Current_Status": "Available" if self.Current_Status == 'A' else "Occupied",
            "Lot_Name": self.belong_to_lot.Location_Name if self.belong_to_lot else None,
            "Created_At": self.Created_At.isoformat() if self.Created_At else None
        }


class ParkingReservation(db.Model):
    __tablename__ = "ParkingReservation"
    
    Reservation_Id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey("VehicleUser.User_id"), nullable=False)
    Spot_Id = db.Column(db.Integer, db.ForeignKey("ParkingSpot.Spot_Id"), nullable=False)
    Vehicle_Number = db.Column(db.String(20), nullable=False)
    Entry_Time = db.Column(db.DateTime, default=lambda: datetime.now(IST), nullable=False)
    Exit_Time = db.Column(db.DateTime, nullable=True)
    Total_Cost = db.Column(db.Float, default=0.0, nullable=True)
    Notes = db.Column(db.String(500), nullable=True)
    Created_At = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    def to_dict(self):
        duration = None
        if self.Entry_Time and self.Exit_Time:
            duration = round((self.Exit_Time - self.Entry_Time).total_seconds() / 3600, 2)
        
        return {
            "Reservation_Id": self.Reservation_Id,
            "User_id": self.User_id,
            "Spot_Id": self.Spot_Id,
            "Spot_Number": self.allocated_spot.Spot_Number if self.allocated_spot else None,
            "Lot_Name": self.allocated_spot.belong_to_lot.Location_Name if self.allocated_spot else None,
            "Vehicle_Number": self.Vehicle_Number,
            "Entry_Time": self.Entry_Time.isoformat() if self.Entry_Time else None,
            "Exit_Time": self.Exit_Time.isoformat() if self.Exit_Time else None,
            "Duration_Hours": duration,
            "Total_Cost": self.Total_Cost,
            "Notes": self.Notes,
            "Created_At": self.Created_At.isoformat() if self.Created_At else None
        }
