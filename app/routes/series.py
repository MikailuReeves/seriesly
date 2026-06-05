from app.db import get_db
from datetime import date
from app.routes.auth import login_required
from flask import Blueprint, render_template, request, flash, session, redirect, url_for, abort

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

    if content is None:
        abort(404)

    if content['is_private'] and content['created_by'] != session['user_id']:
        abort(403)

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

    reviews = db.execute(
        """SELECT r.*, u.username 
           FROM reviews r
           JOIN users u ON r.user_id = u.user_id
           WHERE r.content_id = %s
           ORDER BY r.created_at DESC
        """,
        (content_id,)
    ).fetchall()

    review_count = len(reviews)
    avg_rating = round(sum(r['stars'] for r in reviews) / review_count, 1) if review_count > 0 else None

    return render_template('series_detail.html', content=content, owner=owner, tracking=tracking, progress=progress, reviews=reviews, avg_rating=avg_rating, review_count=review_count)

@bp.route('/<int:content_id>/delete', methods=['POST'])
@login_required
def delete(content_id):
    db = get_db()
    content = db.execute(
        "SELECT * FROM content WHERE content_id = %s",
        (content_id,)
    ).fetchone()

    if content is None:
        abort(404)
    if content['created_by'] != session['user_id'] or not content['is_private']:
        abort(403)

    db.execute("DELETE FROM content WHERE content_id = %s", (content_id,))
    db.commit()
    return redirect(url_for('home.home'))


@bp.route('/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(content_id):
    db = get_db()
    content = db.execute(
        "SELECT * FROM content WHERE content_id = %s",
        (content_id,)
    ).fetchone()

    if content is None:
        abort(404)
    if content['created_by'] != session['user_id'] or not content['is_private']:
        abort(403)

    if request.method == 'GET':
        return render_template('series_edit.html', content=content, current_year=date.today().year)

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

    error = None
    if not name:
        error = "Name is required."
    elif not content_type:
        error = "Type is required."

    if error:
        flash(error)
        return render_template('series_edit.html', content=content, current_year=date.today().year)

    db.execute(
        """UPDATE content SET
            content_name = %s, type = %s, release_year = %s, description = %s,
            cover_url = %s, link_url = %s, total_episodes = %s, total_seasons = %s,
            is_private = true
            WHERE content_id = %s
        """,
        (name, content_type, release_year, description, cover_url, link_url,
         total_episodes, total_seasons, content_id)
    )
    db.commit()
    return redirect(url_for('series.detail', content_id=content_id))
