from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    """Table for registering users"""
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip = db.Column(db.String(5), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(130), nullable=False)
    
    def set_password(self, password):
        """Set the password hash for the user"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        """Check if the passwword matched the hashed password"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @classmethod
    def is_phone_number_email_duplicate(cls, phone_number, email):
        """Check if the phone number or email already exists in the database"""
        existing_user = cls.query.filter((cls.phone_number == phone_number) | (cls.email == email)).first()
        return existing_user is not None
    
class FavoriteDrink(db.Model):
    """Table for storing users' favorite drinks"""

    __tablename__ = "favorite_drinks"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drink_name = db.Column(db.String(100), nullable=False)
    drink_id = db.Column(db.String(50), nullable=False)  
    drink_thumb = db.Column(db.String(200)) 
    
    user = relationship("User", backref=db.backref('favorite_drinks', cascade="all, delete-orphan"))


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)