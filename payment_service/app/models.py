from email.policy import default
from app import db
from datetime import datetime

class Cart(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    
    
class Payment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    timestamp= timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    payment_method = db.Column(db.String(50),default="card")
    status = db.Column(db.Boolean,default=True)