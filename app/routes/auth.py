from functools import wraps

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from psycopg.errors import UniqueViolation
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db


bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
        return

    with get_db().execute(
        "SELECT user_id, username, email FROM users WHERE user_id = %s",
        (user_id,),
    ) as cursor:
        g.user = cursor.fetchone()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/signup", methods=("GET", "POST"))
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        error = None

        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."

        if error is None:
            db = get_db()
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO users (username, email, password_hash)
                        VALUES (%s, %s, %s)
                        RETURNING user_id
                        """,
                        (username, email, generate_password_hash(password)),
                    )
                    user = cursor.fetchone()
                db.commit()
            except UniqueViolation:
                db.rollback()
                error = "That username or email is already in use."
            else:
                session.clear()
                session["user_id"] = user["user_id"]
                return redirect(url_for("home.home"))

        flash(error)

    return render_template("signup.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username_or_email = request.form["username_or_email"].strip()
        password = request.form["password"]
        error = None

        with get_db().execute(
            """
            SELECT user_id, username, email, password_hash
            FROM users
            WHERE lower(username) = lower(%s) OR lower(email) = lower(%s)
            """,
            (username_or_email, username_or_email),
        ) as cursor:
            user = cursor.fetchone()

        if user is None:
            error = "Incorrect username, email, or password."
        elif not check_password_hash(user["password_hash"], password):
            error = "Incorrect username, email, or password."

        if error is None:
            session.clear()
            session["user_id"] = user["user_id"]
            return redirect(url_for("home.home"))

        flash(error)

    return render_template("login.html")


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
