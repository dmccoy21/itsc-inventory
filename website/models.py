from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta


class InventoryIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150))
    item_number = db.Column(db.Integer)
    item_type = db.Column(db.String(75))
    dateIn = db.Column(db.DateTime, index=True, default=func.now())


class InventoryOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150))
    item_type = db.Column(db.String(75))
    item_number = db.Column(db.Integer)
    dateOut = db.Column(db.DateTime, index=True, default=func.now())
    user_email = db.Column(db.String(150))
    returnDate = db.Column(db.DateTime, index=True, default=func.now())


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime, index=True, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(75))
    last_name = db.Column(db.String(75))
    department = db.Column(db.String(150))
    tickets = db.relationship('Ticket')
