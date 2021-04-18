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

    return {'id': cart.id,
            'product': product.id}


def list_all_products(user_id):
    cart = db.session.query(ShoppingCart).filter_by(user_id=user_id).first()
    products = cart.products
    productList = []

    for product in products:
        productList.append({'id': product.product_id,
                            'name': product.name,
                            'price': product.price,
                            'quantity': product.quantity})

    return productList


connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

from models import ShoppingCart, Product

if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
