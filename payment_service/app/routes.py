from app import app, db
from flask import request, jsonify
from app.models import Cart, Payment
import requests
from config import Config


EMPTY_MSG = 'Cart is empty'
PRODUCT_SERVICE_URL = 'http://127.0.0.1:5001/product/'
PAYMENT_SERVICE_URL = 'http://127.0.0.1:5002/cart/'


@app.before_first_request
def create_tables():
    db.create_all()

#add item in your cart
@app.route('/cart/<int:user_id>/<int:product_id>', methods=['POST'])
def add_item_to_cart(user_id, product_id):
    data = request.get_json()
    product = requests.get(PRODUCT_SERVICE_URL + str(product_id)).json()
    
    if data['quantity'] > product['quantity']:
        return {"message": f"Currently required quantity of {product['product_name']} is not available"},404
   
    present_item = Cart.query.filter((Cart.user_id == user_id),(Cart.product_id == product_id)).first()
    
    if present_item:
        present_item.quantity = data['quantity']  
        db.session.commit()
        return {"message":"Item added to cart successfully"}
    
    item = Cart(user_id=user_id, product_id=product_id, quantity=data['quantity'])
    db.session.add(item)
    db.session.commit()
    return {"message":"Item added to cart successfully"}          

         
#View Cart items
@app.route('/cart/<int:user_id>',methods=['GET'])
def get_cart_items(user_id):
    items = Cart.query.filter_by(user_id=user_id).all()
    output=[]
    for item in items:
        data={"product_id":item.product_id,"quantity":item.quantity}
        output.append(data)
    return {"Cart Items":output} 

#Remove One Product from Cart
@app.route('/cart/<int:user_id>/<int:product_id>',methods=['DELETE'])
def delete_cart_item(user_id,product_id):
    item = Cart.query.filter((Cart.user_id==user_id),(Cart.product_id==product_id)).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return {"message":"Item removed from cart"}
    return {"message":"Item doesn't exists"},404

#Remove all products from cart
@app.route('/cart/<int:user_id>',methods=['DELETE'])
def delete_cart_items(user_id):
    items = Cart.query.filter(Cart.user_id==user_id).all()
    if not items:
        return {"message":EMPTY_MSG},404
    for item in items:
        db.session.delete(item)
        db.session.commit()
    return {"message":"All Items  removed from cart"}


#Update quantity of the item
@app.route('/cart/<int:user_id>/<int:product_id>',methods=['PUT'])
def update_cart_item(user_id,product_id):
    item = Cart.query.filter((Cart.user_id==user_id),(Cart.product_id==product_id)).first()
    product = requests.get(PRODUCT_SERVICE_URL+ str(product_id)).json()
    if item:
        data=request.get_json()
        if(data['quantity']>product['quantity']):
            return {"message":f"Currently the required quantity of product {product['product_name']} is not available"}, 404
        item.quantity=data['quantity']
        db.session.commit()
        return {"message":"Quantity Updated"}
    return {"message":"Item doesn't exists"},404


    
    #Purchase All the items in cart
@app.route('/buy/<int:user_id>',methods=['POST'])
def buy_all_cart_items(user_id):
    try:
        cart_items = Cart.query.filter(Cart.user_id==user_id).all()
        if not cart_items:
            return {"message":EMPTY_MSG},404
        total=0
        before_price=0
        data=request.get_json()
        if 'payment_method' in data:
            payment_method=data['payment_method']
        else:
            payment_method=None
        for item in cart_items:
            product_id = item.product_id
            quantity = item.quantity
            product = requests.get(PRODUCT_SERVICE_URL + str(product_id)).json()
            if product['quantity'] < quantity:
                return{"Message":f"Product {product['product_name']} is out of stock "},404
            price = quantity*product['price']
            before_price +=price
            if price>1000 and price<2500:
                price=price-(price*Config.discounts["DISCOUNT5"])
            if price>2500:
                price=price-(price*Config.discounts["DISCOUNT10"])
            total+=price
            item = Payment(user_id=user_id,product_id=product_id,quantity=quantity,price=price,payment_method=payment_method)
            db.session.add(item)
            db.session.commit()
            requests.put(PRODUCT_SERVICE_URL+'quantity/' + str(quantity)+"/"+str(product_id))
        requests.delete(PRODUCT_SERVICE_URL + str(user_id))
        return {"message":f"Transaction successful, Total amount = {before_price}, After discount ={total}"}
    except:
        return {"message":"Some error occured"},409
    
    #View user transactions
@app.route('/transactions/<int:user_id>',methods=['GET'])
def view_transactions(user_id):
    transactions= Payment.query.filter(Payment.user_id==user_id).all()
    if not transactions:
        return {"message":"No transactions found"}, 404
    output=[]
    for item in transactions:
        data={"transaction_id":item.id,"user_id":item.user_id, "product_id": item.product_id, "quantity":item.quantity,"price":item.price,
        "timestamp": item.timestamp,"payment mode": item.payment_method, "status": item.status}
        output.append(data)
    return {"message": output}, 200