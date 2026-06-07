from flask import Blueprint, request, redirect, url_for, session, flash
from app.db import get_db
from app.routes.auth import login_required
import psycopg

bp = Blueprint("reviews", __name__)

@bp.route('/<int:content_id>', methods=['POST'])
@login_required
def submit(content_id):
    stars = request.form.get('stars', type=int)
    body = request.form.get('body', '').strip()

    if not stars or not (1 <= stars <= 5):
        flash("Stars must be between 1 and 5.")
        return redirect(url_for('series.detail', content_id=content_id))

    db = get_db()
    try:
        db.execute(
            """INSERT INTO reviews (user_id, content_id, stars, body)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (user_id, content_id) DO UPDATE SET stars = EXCLUDED.stars, body = EXCLUDED.body
            """,
            (session['user_id'], content_id, stars, body)
        )
        db.commit()
    except psycopg.Error:
        db.rollback()
        flash("Could not submit review.")

    return redirect(url_for('series.detail', content_id=content_id))
