from flask import Flask
from app.routes.client_blueprint import bp_clients
from app.routes.professional_blueprint import bp_professional


def init_app(app: Flask):
    app.register_blueprint(bp_clients)
    app.register_blueprint(bp_professional)