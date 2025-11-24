# user.py
from flask import request, Blueprint
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

from extensions import db, cache
from models import VehicleUser, ParkingLot, ParkingSpot, ParkingReservation
from datetime import datetime
from zoneinfo import ZoneInfo
import math
import json

IST = ZoneInfo('Asia/Kolkata')


class UserDashboard(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()

            # use same key name as other parts of your app
            lots_cached = cache.get('parking_lots_data')
            if lots_cached:
                lots_data = json.loads(lots_cached).get('lots', [])
            else:
                # eager-load spots to reduce queries
                lots = ParkingLot.query.options(joinedload(ParkingLot.available_spots)).all()
                lots_data = [lot.to_dict() for lot in lots]
                cache.set('parking_lots_data', json.dumps({'lots': lots_data}, default=str), timeout=300)

            # get all reservations for this user, eager-load spot -> lot properly
            reservations = ParkingReservation.query.options(
                joinedload(ParkingReservation.allocated_spot).joinedload(ParkingSpot.belong_to_lot)
            ).filter_by(User_id=user_id).order_by(ParkingReservation.Entry_Time.desc()).all()

            reservations_data = [r.to_dict() for r in reservations]

            # active reservation if any
            active = next((r for r in reservations if r.Exit_Time is None), None)
            active_data = [active.to_dict()] if active else []

            return {
                'lots': lots_data,
                'reservations': reservations_data,
                'active_parking': active_data
            }, 200
        except Exception as e:
            return {'message': str(e)}, 500


class BookSpot(Resource):
    @jwt_required()
    def post(self, lot_id):
        try:
            user_id = get_jwt_identity()
            data = request.get_json() or {}

            # Prevent more than one active reservation per user
            existing = ParkingReservation.query.filter_by(User_id=user_id, Exit_Time=None).first()
            if existing:
                return {'message': 'You already have an active reservation'}, 400

            # find first available spot
            spot = ParkingSpot.query.filter_by(Lot_Id=lot_id, Current_Status='A')\
                    .order_by(ParkingSpot.Spot_Id).first()

            if not spot:
                return {'message': 'No available spots'}, 400

            reservation = ParkingReservation(
                User_id=user_id,
                Spot_Id=spot.Spot_Id,
                Vehicle_Number=data.get('Vehicle_Number', ''),
                Entry_Time=datetime.now(IST)
            )

            # mark spot occupied
            spot.Current_Status = 'O'

            db.session.add(reservation)
            db.session.commit()

            # clear caches affected
            cache.delete('parking_lots_data')
            cache.delete(f'user_history_{user_id}')  # if you cache per-user history
            cache.delete('admin_dashboard')

            return {
                'message': 'Spot booked successfully',
                'reservation_id': reservation.Reservation_Id,
                'spot_number': spot.Spot_Number
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400


class ReleaseSpot(Resource):
    @jwt_required()
    def put(self, reservation_id):
        try:
            user_id = get_jwt_identity()

            reservation = ParkingReservation.query.get(reservation_id)
            if not reservation or reservation.User_id != user_id:
                return {'message': 'Reservation not found'}, 404

            if reservation.Exit_Time:
                return {'message': 'Already released'}, 400

            exit_time = datetime.now(IST)

            entry_time = reservation.Entry_Time
            if entry_time is None:
                return {'message': 'Invalid entry time'}, 400

            if entry_time.tzinfo is None:
                entry_time = entry_time.replace(tzinfo=IST)

            duration_seconds = (exit_time - entry_time).total_seconds()
            duration_hours = duration_seconds / 3600.0

            spot = ParkingSpot.query.get(reservation.Spot_Id)
            lot = ParkingLot.query.get(spot.Lot_Id)

            # Billing: round up to next hour
            cost = math.ceil(duration_hours) * float(lot.PRICE)

            reservation.Exit_Time = exit_time
            reservation.Total_Cost = round(cost, 2)

            # mark spot available
            spot.Current_Status = 'A'

            db.session.commit()

            # clear caches
            cache.delete('parking_lots_data')
            cache.delete(f'user_history_{user_id}')
            cache.delete('admin_dashboard')

            return {
                'message': 'Spot released successfully',
                'cost': reservation.Total_Cost,
                'duration_hours': round(duration_hours, 2)
            }, 200
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return {'message': f'Error: {str(e)}'}, 400


class UserHistory(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            cache_key = f'user_history_{user_id}'
            cached = cache.get(cache_key)
            if cached:
                return json.loads(cached), 200

            reservations = ParkingReservation.query.options(
                joinedload(ParkingReservation.allocated_spot).joinedload(ParkingSpot.belong_to_lot)
            ).filter_by(User_id=user_id).order_by(ParkingReservation.Entry_Time.desc()).all()

            res_list = [r.to_dict() for r in reservations]
            cache.set(cache_key, json.dumps({'reservations': res_list}, default=str), timeout=300)
            return {'reservations': res_list}, 200
        except Exception as e:
            return {'message': str(e)}, 500


class ExportHistory(Resource):
    @jwt_required()
    def post(self):
        try:
            from backend.celery_app import export_user_history
            user_id = get_jwt_identity()
            task = export_user_history.delay(user_id)
            return {'message': 'Export started', 'task_id': task.id}, 202
        except Exception as e:
            return {'message': str(e)}, 400


user_bp = Blueprint('user', __name__)
api = Api(user_bp)

api.add_resource(UserDashboard, '/dashboard')
api.add_resource(BookSpot, '/book/<int:lot_id>')
api.add_resource(ReleaseSpot, '/release/<int:reservation_id>')
api.add_resource(UserHistory, '/history')
api.add_resource(ExportHistory, '/export')
