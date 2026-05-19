import os

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
    )

    if test_config is not None:
        app.config.update(test_config)

    from . import db

    db.init_app(app)

    from .routes import auth

    app.register_blueprint(auth.bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app
