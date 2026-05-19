from flask import Blueprint, render_template

from app.routes.auth import login_required

bp = Blueprint("home", __name__)


@bp.route("/")
@login_required
def home():
    return render_template("home.html")
