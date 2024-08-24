from os import environ
from urllib.parse import quote_plus


class AnalysitaConfig:
    ENV: str = environ.get("ENV", "dev")
    FLASK_ENV: str = environ.get("ENV", "development")
    DEBUG: bool = environ.get("DEBUG", True)
    FLASK_DEBUG: bool = environ.get("FLASK_DEBUG", True)

    MONGODB_SETTINGS: dict = environ.get("MONGODB_SETTINGS", {
        "alias": "default",
        "db": environ.get('MONGO_DB_NAME', 'test_db'),
        "host": environ.get('MONGO_HOST', 'localhost'),
        "port": int(environ.get('MONGO_PORT', 27017)),
        "username": environ.get("MONGO_USERNAME", "test_db_user"),
        "password": environ.get("MONGO_PASSWORD", "test_db_password"),
        "authSource": environ.get("authSource", "test_db"),
        "authentication_mechanism": "DEFAULT"
    })

    CELERY_BROKER_URL = environ.get("CELERY_BROKER_URL", default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND_USERNAME = quote_plus(environ.get('MONGO_USERNAME', default="test_db_user"))
    CELERY_RESULT_BACKEND_PASSWORD = quote_plus(environ.get('MONGO_PASSWORD', default="test_db_password"))
    CELERY_RESULT_BACKEND_DB_NAME = environ.get('MONGO_DB_NAME', 'test_db')
    CELERY_RESULT_BACKEND = f'mongodb://{CELERY_RESULT_BACKEND_USERNAME}:{CELERY_RESULT_BACKEND_PASSWORD}@localhost:27017/{CELERY_RESULT_BACKEND_DB_NAME}'
    CELERY_TASK_SERIALIZER = "json"

    CELERY = {
        'broker_url': environ.get("CELERY_BROKER_URL", default='redis://localhost:6379/0'),
        'result_backend': f'mongodb://{CELERY_RESULT_BACKEND_USERNAME}:{CELERY_RESULT_BACKEND_PASSWORD}@localhost:27017/{CELERY_RESULT_BACKEND_DB_NAME}'
    }

    ELASTIC_HOST = environ.get("ELASTIC_HOST", "http://localhost:9200")
    ELASTIC_PASSWORD = environ.get("ELASTIC_PASSWORD", "admin")
    ELASTIC_USERNAME = environ.get("ELASTIC_USERNAME", "elastic")

    @classmethod
    def as_dict(cls):
        return cls.__dict__
