from datetime import datetime
from ..extensions import db


class Shipping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shipping_name = db.Column(db.String(30))
    author_shipping_name = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    driver_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'))  # Внешний ключ на сотрудника
    driver = db.relationship('Employee', backref='shippings')  # Оставляем только этот backref

    destination_point = db.Column(db.String(30))
    starting_point = db.Column(db.String(30))
    vehicle = db.Column(db.String(30))
    date = db.Column(db.DateTime, default=datetime.utcnow)



