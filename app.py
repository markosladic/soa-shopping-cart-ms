import connexion
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def add_product(user_id, product_id):
    product = db.session.query(Product).filter_by(product_id=product_id).first()
    cart = db.session.query(ShoppingCart).filter_by(user_id=user_id).first()
    cart.products.append(product)

    return {'id': cart.id,
            'product': product.id}


def remove_product(user_id, product_id):
    product = db.session.query(Product).filter_by(product_id=product_id).first()
    cart = db.session.query(ShoppingCart).filter_by(user_id=user_id).first()
    cart.products.remove(product)

    return {'cart.id': cart.id,
            'product.id': product.id}


def list_all_products(user_id):
    cart = db.session.query(ShoppingCart).filter_by(user_id=user_id).first()
    products = cart.products
    productList = []

    for product in products:
        productList.append({'product.id': product.product_id,
                            'name': product.name,
                            'price': product.price,
                            'quantity': product.quantity})

    return productList


def change_quantity(user_id, product_id, quantity):
    cart = db.session.query(ShoppingCart).filter_by(user_id=user_id).first()
    product = Product()
    for p in cart.products:
        if p.product_id == product_id:
            p.quantity = quantity
            product = p
            break

    return {
        'product_id': product.product_id,
        'quantity': product.quantity
    }


def buy_products(cart_id):
    cart = db.session.query(ShoppingCart).filter_by(cart_id=cart_id).first()
    price = 0
    for product in cart.products:
        price += (product.price*product.quantity)

    return {
        'price': price
    }


def reserve_product(user_id):
    products = list_all_products(user_id)
    return products


def create_invoice(user_id, transaction_id):
    products = list_all_products(user_id)
    return {'transaction_id': transaction_id,
            'products': products}


#create_order(): ??

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

from models import ShoppingCart, Product

if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
