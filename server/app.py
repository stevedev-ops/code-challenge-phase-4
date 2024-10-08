from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Set up the database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migration
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

class HeroResource(Resource):
    def get(self, id=None):
        if id:
            hero = Hero.query.get(id)
            if hero is None:
                return {'error': 'Hero not found'}, 404
            return hero.to_dict(only=('id', 'name', 'super_name', 'hero_powers'))

        heroes = Hero.query.all()
        return [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes]

class PowerResource(Resource):
    def get(self, id=None):
        if id:
            power = Power.query.get(id)
            if power is None:
                return {'error': 'Power not found'}, 404
            return power.to_dict()

        powers = Power.query.all()
        return [power.to_dict() for power in powers]

    def patch(self, id):
        power = Power.query.get(id)
        if power is None:
            return {'error': 'Power not found'}, 404
        
        data = request.get_json()
        if 'description' in data:
            power.description = data['description']
            try:
                db.session.commit()
                return power.to_dict(), 200
            except Exception as e:  # Catch any exception
                return {'errors': [str(e)]}, 400

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            hero_power = HeroPower(
                hero_id=data['hero_id'],
                power_id=data['power_id'],
                strength=data['strength']
            )
            db.session.add(hero_power)
            db.session.commit()
            return hero_power.to_dict(), 201
        except Exception as e:  # Catch any exception
            return {'errors': [str(e)]}, 400

# Set up the routes
api.add_resource(HeroResource, '/heroes', '/heroes/<int:id>')
api.add_resource(PowerResource, '/powers', '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
