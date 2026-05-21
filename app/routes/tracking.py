from app.db import get_db
from app.routes.auth import login_required
from flask import Blueprint, request, session, redirect, url_for, flash
from psycopg.errors import RaiseException

bp = Blueprint("tracking", __name__)

@bp.route('/<int:content_id>/start', methods=['POST'])
@login_required
def start(content_id):
    db = get_db()
    db.execute(
        "INSERT INTO user_content (user_id, content_id, status) VALUES (%s, %s, 'watching')",
        (session['user_id'], content_id)
    )
    db.commit()
    return redirect(url_for('series.detail', content_id=content_id))

@bp.route('/<int:content_id>/untrack', methods=['POST'])
@login_required
def untrack(content_id):
    db = get_db()
    db.execute(
        """DELETE FROM user_content
           WHERE user_id = %s
           AND content_id = %s
        """,
        (session['user_id'], content_id)
    )
    db.commit()
    return redirect(url_for('series.detail', content_id=content_id))

@bp.route('/<int:content_id>/update', methods=['POST'])
@login_required
def update(content_id):
    db = get_db()
    status = request.form.get('status')
    current_episode = request.form.get('current_episode') or None
    current_season = request.form.get('current_season') or None

    content = db.execute(
        "SELECT * FROM content WHERE content_id = %s",
        (content_id,)
    ).fetchone()

    if status == 'completed' and content['total_episodes']:
        current_episode = content['total_episodes']
        current_season = content['total_seasons']

    try:
        db.execute(
            """UPDATE user_content
            SET status = %s, current_episode = %s, current_season = %s
            WHERE user_id = %s AND content_id = %s
            """,
            (status, current_episode, current_season, session['user_id'], content_id)
        )
        db.commit()
    except RaiseException:
        db.rollback()
        flash("Episode or season cannot exceed the total.")

    return redirect(url_for('series.detail', content_id=content_id))
