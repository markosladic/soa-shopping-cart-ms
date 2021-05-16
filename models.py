from sqlalchemy.orm import relationship

from app import db
from enum import Enum


class Status(Enum):
    CREATED = 0
    CANCELED = 1
    FINISHED = 2


class ShoppingCart(db.Model):
    __tablename__ = 'shopping_cart'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    status = db.Column(db.Enum(Status), nullable=False)
    isPriority = db.Column(db.Boolean, nullable=False)
    product_id = relationship("Product")
    user = relationship("User")


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)


class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('shopping_cart.user_id'))
