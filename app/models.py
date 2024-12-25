# models.py
from . import db  # Import from app/__init__.py
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'professional'
    address = db.Column(db.String(100), nullable= False)
    pin_code = db.Column(db.String(6), nullable = False)
    contact_no = db.Column(db.String(10), nullable = True)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    services = db.relationship('Service', back_populates='category')

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', name='fk_service_category'), nullable=False)
    # professional = db.Column(db.String(100), nullable=True)
    professional_email = db.Column(db.String(100), db.ForeignKey('professionals.email', name='fk_service_professional'), nullable=True)
    rate = db.Column(db.Float, nullable=True)
    professional = db.relationship('Professional', back_populates='services')
    category = db.relationship('Category', back_populates='services')

    

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_service_request_customer'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_service_request_professional'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', name='fk_service_request_service'), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    date_of_request = db.Column(db.DateTime , server_default=func.now())
    status = db.Column(db.String(20), nullable=False)  # 'requested', 'assigned', 'closed'
    remarks = db.Column(db.Text)
    rate = db.Column(db.Float, nullable=True)

    customer = db.relationship('User', foreign_keys=[customer_id])
    professional = db.relationship('User', foreign_keys=[professional_id])
    service = db.relationship('Service')

class Professional(db.Model):
    __tablename__ = 'professionals'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'professional'
    service = db.Column(db.String(100), nullable= False)
    pin_code = db.Column(db.String(6), nullable = False)
    contact_no = db.Column(db.String(10), nullable = True)
    expireance = db.Column(db.Integer, nullable = False)
    people = db.Column(db.Integer, nullable = False, default=1)
    base_price = db.Column(db.Float, nullable = False)
    city = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    rate = db.Column(db.Float, nullable=True, default=0.0)

    services = db.relationship('Service', back_populates='professional')
        