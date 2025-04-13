from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    pizzas = db.relationship('Pizza', secondary='restaurant_pizzas', back_populates='restaurants', overlaps='restaurant_pizzas')
    
    # add serialization rules
    def to_dict(self, include_pizzas=True, include_rp=False):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }

        if include_pizzas:
            data['pizzas'] = [pizza.to_dict_simple() for pizza in self.pizzas]

        if include_rp:
            data['restaurant_pizzas'] = [rp.to_dict() for rp in self.restaurant_pizzas]

        return data

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan', overlaps='pizzas')
    restaurants = db.relationship('Restaurant', secondary='restaurant_pizzas', back_populates='pizzas', overlaps='restaurant_pizzas')

    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'restaurants': [restaurant.name for restaurant in self.restaurants]
        }

    def to_dict_simple(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)


    # add relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas", overlaps='pizzas,restaurants')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas', overlaps='pizzas,restaurants')
    
    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'pizza': self.pizza.to_dict_simple() if self.pizza else None,
            'restaurant': self.restaurant.to_dict() if self.restaurant else None
        }


    # add validation
    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError('Price must be between 1 and 30.')
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
