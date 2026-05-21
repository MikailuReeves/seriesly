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
    total_episodes_raw = request.form.get('total_episodes')
    total_episodes = int(total_episodes_raw) if total_episodes_raw else None
    total_seasons_raw = request.form.get('total_seasons')
    total_seasons = int(total_seasons_raw) if total_seasons_raw else None
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
        return render_template('series_add.html', current_year=date.today().year)

    db = get_db()
    cursor = db.execute(
        """INSERT INTO content
            (content_name, created_by, type, release_year, description,
            cover_url, link_url, total_episodes, total_seasons,
            is_private)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING content_id
        """,
        (name, session['user_id'], content_type, release_year, description,
        cover_url, link_url, total_episodes, total_seasons, is_private)
    )
    content_id = cursor.fetchone()['content_id']
    db.commit()
    return redirect(url_for('series.detail', content_id=content_id))

# Series Details page
@bp.route('/<int:content_id>')
@login_required
def detail(content_id):
    db = get_db()
    content = db.execute(
        "SELECT * FROM content WHERE content_id = %s",
        (content_id,)
    ).fetchone()

    owner = db.execute(
        "SELECT username FROM users WHERE user_id = %s",
        (content['created_by'],)
    ).fetchone()

    tracking = db.execute(
        "SELECT * FROM user_content WHERE user_id = %s AND content_id = %s",
        (session['user_id'], content_id)
    ).fetchone()

    progress = 0
    if tracking:
        if tracking['status'] == 'completed':
            progress = 100
        elif content['total_episodes'] and tracking['current_episode']:
            progress = round(tracking['current_episode'] / content['total_episodes'] * 100)

    return render_template('series_detail.html', content=content, owner=owner, tracking=tracking, progress=progress)
