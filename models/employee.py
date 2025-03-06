from ..extensions import db, login_manager
from datetime import datetime


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    date_hired = db.Column(db.DateTime, default=datetime.utcnow)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(120), nullable=True)




