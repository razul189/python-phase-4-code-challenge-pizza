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

# @app.route("/")
# def index():
#     return "<h1>Code challenge</h1>"

class Index(Resource):
    def get(self):
        response_dict = {"message": "Welcome to the Pizza Restaurant API"}
        return make_response(response_dict, 200)

api.add_resource(Index, '/')

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurants_data = [r.to_dict(only=("id", "name", "address")) for r in restaurants]
        return make_response(restaurants_data, 200)

api.add_resource(RestaurantsResource, '/restaurants')


class RestaurantDetailResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
       
        return make_response(restaurant.to_dict(), 200)
    

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        
        return make_response("", 204)

api.add_resource(RestaurantDetailResource, '/restaurants/<int:id>')

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizzas_data = [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas]
        return make_response(pizzas_data, 200)

api.add_resource(PizzasResource, '/pizzas')


class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_rp = RestaurantPizza(
                price=data.get("price"),
                pizza_id=data.get("pizza_id"),
                restaurant_id=data.get("restaurant_id")
            )
            db.session.add(new_rp)
            db.session.commit()
            return make_response(new_rp.to_dict(), 201)
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
