from flask import Blueprint, render_template, request, session
from app.db import get_db
from app.routes.auth import login_required
import psycopg

bp = Blueprint("search", __name__)

@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    results = []
    error = None

    if q:
        db = get_db()
        try:
            results = db.execute(
                """
                SELECT c.*, u.username
                FROM content c
                JOIN users u ON c.created_by = u.user_id
                WHERE c.content_name ~* %s
                  AND (NOT c.is_private OR c.created_by = %s)
                ORDER BY c.content_name ASC
                """,
                (q, session['user_id'])
            ).fetchall()
        except psycopg.errors.DataError:
            # Handle invalid regex
            error = "Invalid search query."
            db.rollback()

    return render_template("search.html", results=results, q=q, error=error)
