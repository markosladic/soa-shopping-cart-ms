from app import db
from enum import Enum


class Status(Enum):
    CREATED = 0
    CANCELED = 1
    FINISHED = 2


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status), nullable=False)
    isPriority = db.Column(db.Boolean, nullable=False)
    products = db.Column(db.ARRAY(db.Integer), nullable=False)