from app.db import get_db
from flask import Blueprint, render_template, session, request

from app.routes.auth import login_required

bp = Blueprint("home", __name__)


@bp.route("/")
@login_required
def home():
    db = get_db()
    # query for user's tracked content
    my_content = db.execute(
        """
        SELECT c.*, uc.status, uc.current_episode, uc.current_season
        FROM user_content uc
        JOIN content c ON c.content_id = uc.content_id
        WHERE uc.user_id = %s
        ORDER BY c.content_name
        """, (session['user_id'],)).fetchall()

    # query for public content
    public_content = db.execute(
        """
        SELECT c.*, u.username, ROUND(AVG(r.stars), 1) as avg_rating
        FROM content c
        JOIN users u ON u.user_id = c.created_by
        LEFT JOIN reviews r ON r.content_id = c.content_id
        WHERE c.is_private = false
        GROUP BY c.content_id, u.username
        ORDER BY c.content_name
        """).fetchall()

    for item in my_content:
        if item['total_episodes'] and item['current_episode']:
            item['progress'] = round(item['current_episode'] / item['total_episodes'] * 100)
        else:
            item['progress'] = 0

    return render_template("home.html", my_content=my_content, public_content=public_content)
