#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]

    return make_response(restaurants, 200)

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurants_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()

    if request.method == 'GET':
        if restaurant:
            return make_response(restaurant.to_dict(include_rp=True), 200)
        else:
            return {'error': 'Restaurant not found'}, 404

    elif request.method == 'DELETE':
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        
        db.session.delete(restaurant)
        db.session.commit()

        return make_response({}, 204)
    
@app.route('/pizzas')
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]

    return make_response(pizzas, 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def new_restaurant_pizza():
    data = request.get_json()

    required_fields = ['price', 'pizza_id', 'restaurant_id']
    if not all(field in data for field in required_fields):
        return {'errors': ['validation errors']}
    
    try: 
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        return make_response(new_restaurant_pizza.to_dict(), 201)
    except Exception:
        return {'errors': ['validation errors']}, 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
