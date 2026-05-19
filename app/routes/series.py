from app.db import get_db
from datetime import date
from app.routes.auth import login_required
from flask import Blueprint, render_template, request, flash, session, redirect, url_for

bp = Blueprint("series", __name__)

@bp.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('series_add.html', current_year=date.today().year)

    # post
    name = request.form.get('content_name', '').strip()
    content_type = request.form.get('type', '')
    release_year = request.form.get('release_year') or None
    description = request.form.get('description', '').strip() or None
    cover_url = request.form.get('cover_url', '').strip() or None
    link_url = request.form.get('link_url', '').strip() or None
    total_episodes = request.form.get('total_episodes') or None
    total_seasons = request.form.get('total_seasons') or None
    is_private = request.form.get('is_private') == 'on'

    error = None
    if not name:
        error = "Name is required."
    elif not content_type:
        error = "Type is required."
    elif content_type == 'youtube' and not link_url:
        error = "Link is required for YouTube content."

    if error:
        flash(error)
        return render_template('series_add.html')

    db = get_db()
    db.execute(
        """INSERT INTO content
            (content_name, created_by, type, release_year, description,
            cover_url, link_url, total_episodes, total_seasons,
            is_private)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (name, session['user_id'], content_type, release_year, description,
        cover_url, link_url, total_episodes, total_seasons, is_private)
    )

    db.commit()
    return redirect(url_for('home.home'))
