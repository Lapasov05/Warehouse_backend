from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    Text, TIMESTAMP, DECIMAL, UniqueConstraint,
    Enum, MetaData, Boolean, Float, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()
metadata = MetaData()


class User(Base):
    __tablename__ = 'user'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    phone = Column(String(20), unique=True, nullable=True)
    password = Column(String)
    role_id = Column(Integer, ForeignKey('role.id'), default=1)
    registration_at = Column(Date, default=datetime.utcnow)
    UniqueConstraint('username', 'email', 'phone', name='unique_username_email_phone')


class Role(Base):
    __tablename__ = 'role'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Product(Base):
    __tablename__ = 'product'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Float)
    amount = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'))
    joined_at = Column(TIMESTAMP, default=datetime.utcnow)


class Category(Base):
    __tablename__ = 'category'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Customer(Base):
    __tablename__ = 'customer'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    email = Column(String, nullable=True)


class Shopping_cart(Base):
    __tablename__ = 'shopping_cart'
    metadata = metadata
    id = Column(Integer, autoincrement=True, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    amount = Column(Integer)
    total = Column(Float)
    is_active = Column(Boolean)


class Order(Base):
    __tablename__ = 'order'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    user_id = Column(Integer, ForeignKey('user.id'))
    is_active = Column(Boolean, default=True)


class Debts(Base):
    __tablename__ = 'Debts'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    paid = Column(Float)
    should_pay = Column(Float)
    total = Column(Float)


class Warehouse(Base):
    __tablename__ = "warehouse"
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    latitude = Column('latitude', Float)
    longitude = Column('longitude', Float)


class Warehouse_category(Base):
    __tablename__ = "warehouse_category"
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(ForeignKey('warehouse.id'))
    category_id = Column(ForeignKey('category.id'))


# class Product_History(Base):
