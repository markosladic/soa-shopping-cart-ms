from functools import wraps
import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from consul import Consul, Check

JWT_SECRET = 'SHOPPING CART MS SECRET'
JWT_LIFETIME_SECONDS = 600000
consul_port = 8500
service_name = "shopping_cart"
service_port = 5002


def register_to_consul():
    consul = Consul(host="consul", port=consul_port)
    agent = consul.agent
    service = agent.service
    check = Check.http(f"http://{service_name}:{service_port}/", interval="10s", timeout="5s", deregister="1s")
    service.register(service_name, service_id=service_name, port=service_port, check=check)


def get_service(service_id):
    consul = Consul(host="consul", port=consul_port)
    agent = consul.agent
    service_list = agent.services()
    service_info = service_list[service_id]
    return service_info['Address'], service_info['Port']


# register_to_consul()


def has_role(arg):
    def has_role_inner(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                headers = request.headers
                if 'AUTHORIZATION' in headers:
                    token = headers['AUTHORIZATION'].split(' ')[1]
                    decoded_token = decode_token(token)
                    if 'admin' in decoded_token['roles']:
                        return fn(*args, **kwargs)
                    for role in arg:
                        if role in decoded_token['roles']:
                            return fn(*args, **kwargs)
                    abort(401)
                return fn(*args, **kwargs)
            except Exception as e:
                abort(401)

        return decorated_view

    return has_role_inner


def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])


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


# @has_role(['shopping_cart', 'user', 'inventory'])
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
        price += (product.price * product.quantity)

    return {
        'price': price,
        'products': cart.products
    }


def reserve_product(user_id):
    products = list_all_products(user_id)
    return products


def create_invoice(user_id, transaction_id):
    products = list_all_products(user_id)
    return {'transaction_id': transaction_id,
            'products': products}


connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

from models import ShoppingCart, Product, Status

if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
