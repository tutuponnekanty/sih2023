from applications.database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import date

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    aadhar_number = db.Column(db.String(20))
    pan_number = db.Column(db.String(10))
    license_id = db.Column(db.String(20))
    license_type = db.Column(db.String(50))
    company_name = db.Column(db.String(120))

    is_retailer = db.Column(db.Boolean, default=False)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='products')


    def __repr__(self):
        return f'<Product {self.name}>'


class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.Date, nullable=False, default=date.today)
