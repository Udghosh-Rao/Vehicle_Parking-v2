from flask import request, Blueprint
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, cache
from models import ParkingLot, ParkingSpot, VehicleUser, ParkingReservation
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from sqlalchemy import func


IST = ZoneInfo('Asia/Kolkata')


class AdminDashboard(Resource):
    @jwt_required()
    def get(self):
        try:
            # Check cache first
            cached = cache.get('admin_dashboard')
            if cached:
                return json.loads(cached), 200
            
            lots = ParkingLot.query.all()
            total_lots = len(lots)
            available = sum(sum(1 for s in lot.available_spots if s.Current_Status == 'A') for lot in lots)
            occupied = sum(sum(1 for s in lot.available_spots if s.Current_Status == 'O') for lot in lots)
            
            reservations = ParkingReservation.query.all()
            revenue = sum(r.Total_Cost for r in reservations if r.Total_Cost)
            
            result = {
                'stats': {
                    'total_lots': total_lots,
                    'available': available,
                    'occupied': occupied,
                    'total_revenue': revenue
                }
            }
            
            # Store in cache (5 minutes)
            cache.set('admin_dashboard', json.dumps(result), timeout=300)
            
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 500


class LotList(Resource):
    @jwt_required()
    def get(self):
        try:
            # Check cache first
            cached = cache.get('parking_lots_list')
            if cached:
                return json.loads(cached), 200
            
            lots = ParkingLot.query.all()
            result = {
                'lots': [lot.to_dict() for lot in lots]
            }
            
            # Store in cache (5 minutes)
            cache.set('parking_lots_list', json.dumps(result, default=str), timeout=300)
            
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 500

    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            
            lot = ParkingLot(
                Location_Name=data.get('Location_Name'),
                Address_name=data.get('Address_name'),
                PRICE=data.get('PRICE'),
                Maximum_Number_Spots=data.get('Maximum_Number_Spots')
            )
            
            db.session.add(lot)
            db.session.flush()
            
            # Create parking spots
            for i in range(1, data.get('Maximum_Number_Spots', 0) + 1):
                spot = ParkingSpot(
                    Lot_Id=lot.id,
                    Spot_Number=f'A{i}',
                    Current_Status='A'
                )
                db.session.add(spot)
            
            db.session.commit()
            
            # Clear cache
            cache.delete('parking_lots_list')
            cache.delete('admin_dashboard')
            
            return {'message': 'Lot created successfully', 'lot_id': lot.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error: {str(e)}'}, 400


class LotDetail(Resource):
    @jwt_required()
    def get(self, lot_id):
        """Get single lot details"""
        try:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return {'message': 'Lot not found'}, 404
            return lot.to_dict(), 200
        except Exception as e:
            return {'message': str(e)}, 500
    
    @jwt_required()
    def put(self, lot_id):
        """Update lot - increase/decrease spots"""
        try:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return {'message': 'Lot not found'}, 404
            
            data = request.get_json()
            new_max = data.get('Maximum_Number_Spots')
            
            if new_max:
                current_count = len(lot.available_spots)
                occupied_count = sum(1 for s in lot.available_spots if s.Current_Status == 'O')
                
                # Validate: cannot reduce below occupied count
                if new_max < occupied_count:
                    return {'message': f'Cannot reduce below {occupied_count} occupied spots'}, 400
                
                # Increase spots
                if new_max > current_count:
                    for i in range(current_count + 1, new_max + 1):
                        spot = ParkingSpot(
                            Lot_Id=lot.id,
                            Spot_Number=f'A{i}',
                            Current_Status='A'
                        )
                        db.session.add(spot)
                
                # Decrease spots (only remove empty ones)
                elif new_max < current_count:
                    spots_to_remove = ParkingSpot.query.filter_by(
                        Lot_Id=lot_id,
                        Current_Status='A'
                    ).order_by(ParkingSpot.Spot_Id.desc()).limit(current_count - new_max).all()
                    
                    for spot in spots_to_remove:
                        db.session.delete(spot)
                
                lot.Maximum_Number_Spots = new_max
            
            # Update other fields
            if 'Location_Name' in data:
                lot.Location_Name = data['Location_Name']
            if 'Address_name' in data:
                lot.Address_name = data['Address_name']
            if 'PRICE' in data:
                lot.PRICE = data['PRICE']
            
            db.session.commit()
            
            # Clear cache
            cache.delete('parking_lots_list')
            cache.delete('admin_dashboard')
            
            return {'message': 'Lot updated successfully', 'lot': lot.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400
    
    # Keep your existing delete method
    @jwt_required()
    def delete(self, lot_id):
        try:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return {'message': 'Lot not found'}, 404
            
            # Check if all spots are empty
            occupied = sum(1 for s in lot.available_spots if s.Current_Status == 'O')
            if occupied > 0:
                return {'message': f'Cannot delete lot with {occupied} occupied spots'}, 400
            
            db.session.delete(lot)
            db.session.commit()
            
            cache.delete('parking_lots_list')
            cache.delete('admin_dashboard')
            
            return {'message': 'Lot deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400



class UserList(Resource):
    @jwt_required()
    def get(self):
        try:
            # Check cache first
            cached = cache.get('users_list')
            if cached:
                return json.loads(cached), 200
            
            users = VehicleUser.query.filter_by(Role='user').all()
            user_list = []
            for user in users:
                booking_count = ParkingReservation.query.filter_by(User_id=user.User_id).count()
                user_list.append({
                    'User_id': user.User_id,
                    'Full_Name': user.Full_Name,
                    'Email_Address': user.Email_Address,
                    'Phone_Number': user.Phone_Number,
                    'total_bookings': booking_count
                })
            
            result = {'users': user_list}
            
            # Store in cache (5 minutes)
            cache.set('users_list', json.dumps(result), timeout=300)
            
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 500

class AdminAnalytics(Resource):
    @jwt_required()
    def get(self):
        """Get analytics data for charts"""
        try:
            # Parking by lot
            lots = ParkingLot.query.all()
            lot_data = []
            for lot in lots:
                reservations = ParkingReservation.query.join(ParkingSpot).filter(
                    ParkingSpot.Lot_Id == lot.id
                ).count()
                lot_data.append({
                    'name': lot.Location_Name,
                    'count': reservations
                })
            
            # Revenue by lot
            revenue_data = []
            for lot in lots:
                revenue = db.session.query(func.sum(ParkingReservation.Total_Cost)).join(
                    ParkingSpot
                ).filter(ParkingSpot.Lot_Id == lot.id).scalar() or 0
                revenue_data.append({
                    'name': lot.Location_Name,
                    'revenue': float(revenue)
                })
            
            # Occupancy over time (last 7 days)
            occupancy_data = []
            for i in range(7):
                date = datetime.now(IST).date() - timedelta(days=6-i)
                count = ParkingReservation.query.filter(
                    func.DATE(ParkingReservation.Entry_Time) == date
                ).count()
                occupancy_data.append({
                    'date': date.strftime('%d/%m'),
                    'count': count
                })
            
            # Current status
            total_spots = db.session.query(func.count(ParkingSpot.Spot_Id)).scalar() or 0
            occupied_spots = db.session.query(func.count(ParkingSpot.Spot_Id)).filter(
                ParkingSpot.Current_Status == 'O'
            ).scalar() or 0
            available_spots = total_spots - occupied_spots
            
            status_data = [
                {'name': 'Available', 'value': available_spots},
                {'name': 'Occupied', 'value': occupied_spots}
            ]
            
            return {
                'lot_usage': lot_data,
                'revenue_by_lot': revenue_data,
                'occupancy_trend': occupancy_data,
                'current_status': status_data
            }, 200
        except Exception as e:
            return {'message': str(e)}, 500

class ActiveParkings(Resource):
    @jwt_required()
    def get(self):
        """Get all currently parked vehicles with details"""
        try:
            active = ParkingReservation.query.filter_by(Exit_Time=None).all()
            result = []
            
            for reservation in active:
                duration_hours = (datetime.now(IST) - reservation.Entry_Time).total_seconds() / 3600
                
                result.append({
                    'Reservation_Id': reservation.Reservation_Id,
                    'User_Name': reservation.customer_booking.Full_Name,
                    'User_Phone': reservation.customer_booking.Phone_Number,
                    'Vehicle_Number': reservation.Vehicle_Number,
                    'Lot_Name': reservation.allocated_spot.belong_to_lot.Location_Name,
                    'Spot_Number': reservation.allocated_spot.Spot_Number,
                    'Entry_Time': reservation.Entry_Time.isoformat(),
                    'Duration_Hours': round(duration_hours, 2),
                    'Current_Cost': round(duration_hours * reservation.allocated_spot.belong_to_lot.PRICE, 2)
                })
            
            return {'active_parkings': result}, 200
        except Exception as e:
            return {'message': str(e)}, 500


class ReservationList(Resource):
    @jwt_required()
    def get(self):
        try:
            # Check cache first
            cached = cache.get('reservations_list')
            if cached:
                return json.loads(cached), 200
            
            reservations = ParkingReservation.query.all()
            result = {
                'reservations': [res.to_dict() for res in reservations]
            }
            
            # Store in cache (5 minutes)
            cache.set('reservations_list', json.dumps(result, default=str), timeout=300)
            
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 500


# Create blueprint
admin_bp = Blueprint('admin', __name__)
api = Api(admin_bp)


# Register resources
api.add_resource(AdminDashboard, '/dashboard')
api.add_resource(LotList, '/lots')
api.add_resource(LotDetail, '/lots/<int:lot_id>')
api.add_resource(UserList, '/users')
api.add_resource(ReservationList, '/reservations')
api.add_resource(AdminAnalytics, '/analytics')
api.add_resource(ActiveParkings, '/active-parkings')
