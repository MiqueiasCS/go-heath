from flask import Flask
from app.routes.client_blueprint import bp_clients
from app.routes.professional_blueprint import bp_professional
from app.routes.food_plan_blueprint import bp_food_plan
from app.routes.professional_rating_blueprint import bp_professional_rating
from app.routes.login_blueprint import bp_login


def init_app(app: Flask):
    app.register_blueprint(bp_clients)
    app.register_blueprint(bp_professional)
    app.register_blueprint(bp_food_plan)
    app.register_blueprint(bp_professional_rating)
    app.register_blueprint(bp_login)
