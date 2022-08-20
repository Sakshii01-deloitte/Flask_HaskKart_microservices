from app import app,db
from flask import request,jsonify
from app.models import Products

@app.before_first_request
def create_tables():
    db.create_all()



#Add new product (only admin)
@app.route('/product/<int:user_id>',methods=['POST'])
def add_product(user_id):
    data = request.get_json()
    print("init")
    new_product = Products(product_name=data['product_name'],
                           price=data['price'],
                           ratings=data['ratings'],
                           description=data['description'],
                           category=data['category'],
                           quantity=data['quantity'],
                           user_id=user_id)
    print("new product",new_product)
    print("new product",new_product.ratings)
    db.session.add(new_product)
    db.session.commit()
    return {"message":"Data added successfully"},201


#user can fetch product
@app.route('/product/<int:id>')
def get_product(id):
    product = Products.query.filter_by(id=id).first()
    if product:
        response={"product_name":product.product_name,
                    "price":product.price,
                    "ratings":product.ratings,
                    "category":product.category,
                    "description":product.description,
                    "quantity":product.quantity,
                    "id":product.id}
        return response,200
    return {"message":"coudent find product"},404