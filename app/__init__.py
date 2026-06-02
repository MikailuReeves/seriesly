import os

from flask import Flask
from .routes import auth, home, series, tracking, search, reviews
from . import db

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
    )

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(tracking.bp, url_prefix='/tracking')
    app.register_blueprint(series.bp, url_prefix='/series')
    app.register_blueprint(search.bp, url_prefix='/search')
    app.register_blueprint(reviews.bp, url_prefix='/reviews')

    return app
