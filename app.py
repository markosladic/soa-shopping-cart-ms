from functools import wraps
import connexion
import jwt
from consul import Consul, Check
from flask import request, abort
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

JWT_SECRET = 'SHOPPING CART MS SECRET'
JWT_LIFETIME_SECONDS = 600000
consul_port = 8500
service_name = "sc"
service_port = 5000


def register_to_consul():
    consul = Consul(host='consul', port=consul_port)
    agent = consul.agent
    service = agent.service
    check = Check.http(f"http://{service_name}:{service_port}/api/ui", interval="10s", timeout="5s", deregister="1s")
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


def create_shopping_cart(user_id):
    sc = ShoppingCart(user_id=user_id, status=Status.CREATED, isPriority=False)
    db.session.add(sc)
    db.session.commit()

    return {
        'user_id': user_id
    }


def create_user():
    user = User(user_id=2, username="GJ")
    db.session.add(user)
    db.session.commit()

    return {
        'user_id': user.user_id
    }


def create_product():
    product = Product(product_id=1, name="Skopsko", price=100.0, quantity=3, user_id=2)
    db.session.add(product)
    db.session.commit()


# @has_role(['shopping_cart', 'user', 'admin'])
def add_product(user_id, product_id): #trebit user_id i status na inventory(nie im prakjame)
    cart = db.session.query(ShoppingCart).filter_by(user_id=user_id).first()
    product = db.session.query(Product).filter_by(product_id=product_id).first()
    product.user_id = cart.user_id

    db.session.add(cart)
    db.session.commit()

    return {'user_id': user_id,
            'product_id': product_id}


# @has_role(['shopping_cart', 'user', 'admin'])
def remove_product(user_id, product_id):
    carts = db.session.query(ShoppingCart).filter_by(user_id=user_id).all()
    cart = None
    for c in carts:
        if c.product_id is None:
            c.product_id = product_id
            cart = c
            break

    db.session.delete(cart)
    db.session.commit()

    return {'user_id': user_id,
            'product_id': product_id}


# @has_role(['shopping_cart', 'user', 'admin'])
def list_all_products(user_id):
    carts = db.session.query(ShoppingCart).filter_by(user_id=user_id).all()
    products = []
    for cart in carts:
        product = db.session.query(Product).filter_by(product_id=cart.product_id).first()
        products.append({
            'product_id': product.product_id,
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity,
        })

    return products


# @has_role(['shopping_cart', 'user', 'admin'])
def change_quantity(user_id, product_id, quantity):
    cart = db.session.query(ShoppingCart).filter_by(user_id=user_id).first()
    product = None
    for p in cart.products:
        if p.product_id == product_id:
            p.quantity = quantity
            product = p
            break

    return {
        'product_id': product.product_id,
        'quantity': product.quantity
    }


# @has_role(['shopping_cart', 'user', 'admin'])
def buy_products(user_id):
    carts = db.session.query(ShoppingCart).filter_by(user_id=user_id).all()
    price = 0
    for cart in carts:
        product = db.session.query(Product).filter_by(product_id=cart.product_id).first()
        price += product.price * product.quantity

    return {
        'price': price
    }


# @has_role(['shopping_cart', 'user', 'admin', 'invoices'])
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

from models import ShoppingCart, Product, Status, User

# register_to_consul()

if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
