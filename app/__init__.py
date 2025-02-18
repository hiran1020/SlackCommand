from flask import Flask
from .dumpdb import dumpdb  # Import routes after the app is created

def create_app():
    app = Flask(__name__)

    # Initialize extensions, configuration, etc.
    # app.config.from_object('config.Config')

    # Register blueprints (your routes)
    app.register_blueprint(dumpdb)

    return app
