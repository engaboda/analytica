import logging

from flask import Flask
from flask_restful import Api

from src.celery import celery_init_app
from src.config import AnalysitaConfig
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from src.routers import routers

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.logger.setLevel(logging.INFO)

if not app.debug:
    # Set the log level to info to ensure all messages are captured.
    # Create a file handler to write logs to a file.
    file_handler = logging.FileHandler('application.log')

    # Set a format for the logs.
    file_handler.setFormatter(
        logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    )

    # Add the file handler to the app's logger.
    app.logger.addHandler(file_handler)

app.config.from_object(AnalysitaConfig)

api_app = Api(app)
db = MongoEngine()
db.init_app(app)

celery_app = celery_init_app(app)

routers(api_app)
