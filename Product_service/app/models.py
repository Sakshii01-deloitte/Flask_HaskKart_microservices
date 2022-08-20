from app import db

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120))
    price = db.Column(db.Float)
    ratings = db.Column(db.Integer)
    category = db.Column(db.String(120))
    description = db.Column(db.String(120))
    quantity = db.Column(db.Integer)
    