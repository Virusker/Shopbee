from sqlalchemy import Integer, String, Column, DateTime, Boolean,ForeignKey
from flask_login import UserMixin
from enum import Enum as UserEnum
from app import db
from datetime import datetime
class BaseModel(db.Model, UserMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True , autoincrement=True)

class UserRoles(UserEnum):
    ADMIN = 0
    USER = 1

class Delivery(UserEnum):
    NORMAL = 0
    FAST = 1
    VERRY_FAST = 2

class Payment(UserEnum):
    COD = 0
    VISA = 1
    MOMO = 2


class User(BaseModel):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)
    avatar = Column(String(255))
    role = Column(Integer, default=UserRoles.USER)

class UserDetail(BaseModel):
    __tablename__ = 'user_details'
    user_id = Column(Integer, ForeignKey('users.id'))
    address = Column(String(255))
    district = Column(String(255))
    city = Column(String(255))
    user = db.relationship('User', backref='user_detail', lazy=True)

class Category(BaseModel):
    __tablename__ = 'categories'
    name = Column(String(255))
    description = Column(String(255))
    products = db.relationship('Product', backref='category', lazy=True)

class Product(BaseModel):
    __tablename__ = 'products'
    name = Column(String(255),nullable=False)
    avatar = Column(String(255))
    description = Column(String(255))
    price = Column(Integer)
    created_at = Column(DateTime,default=datetime.now)
    updated_at = Column(DateTime,default=datetime.now)
    active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey('categories.id'))

class Cart(BaseModel):
    __tablename__ = 'carts'
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    total = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    product = db.relationship('Product', backref='cart', lazy=True)

class Order(BaseModel):
    __tablename__ = 'orders'
    user_id = Column(Integer, ForeignKey('users.id'))
    total = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    status = Column(Integer, default=0)

class OrderDetail(BaseModel):
    __tablename__ = 'order_details'
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    total = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    product = db.relationship('Product', backref='order_detail', lazy=True)
    order = db.relationship('Order', backref='order_detail', lazy=True)