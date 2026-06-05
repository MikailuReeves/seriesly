from dotenv import load_dotenv
load_dotenv()

import os
import psycopg
import psycopg.rows
from werkzeug.security import generate_password_hash

DATABASE_URL = os.environ["DATABASE_URL"]

USERS = [
    {"username": "alice",  "email": "alice@example.com",  "password": "password123"},
    {"username": "bob",    "email": "bob@example.com",    "password": "password123"},
    {"username": "carol",  "email": "carol@example.com",  "password": "password123"},
]

CONTENT = [
    {
        "key": "breaking_bad",
        "content_name": "Breaking Bad",
        "type": "tv",
        "release_year": 2008,
        "total_seasons": 5,
        "total_episodes": 62,
        "description": "A high school chemistry teacher diagnosed with terminal cancer partners with a former student to manufacture methamphetamine, descending into the criminal underworld.",
        "cover_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOcWkpWG_NRrU2M8-WB8EbEcJk7smhdrY1eO0ttKXm0bo2ooOEWxk3zBSbsFrSgSJh2OEKOQ&s=10",
        "link_url": None,
        "is_private": False,
        "created_by": "alice",
    },
    {
        "key": "inception",
        "content_name": "Inception",
        "type": "movie",
        "release_year": 2010,
        "total_seasons": None,
        "total_episodes": None,
        "description": "A skilled thief is offered a chance to have his criminal record erased if he can successfully plant an idea into a CEO's subconscious.",
        "cover_url": "https://m.media-amazon.com/images/M/MV5BZjhkNjM0ZTMtNGM5MC00ZTQ3LTk3YmYtZTkzYzdiNWE0ZTA2XkEyXkFqcGc@._V1_.jpg",
        "link_url": None,
        "is_private": False,
        "created_by": "bob",
    },
    {
        "key": "aot",
        "content_name": "Attack on Titan",
        "type": "anime",
        "release_year": 2013,
        "total_seasons": 4,
        "total_episodes": 87,
        "description": "Humanity lives behind enormous walls to survive giant humanoid Titans. When the walls are breached, a young boy vows to wipe out every last Titan.",
        "cover_url": "https://static.posters.cz/image/750/22808.jpg",
        "link_url": None,
        "is_private": False,
        "created_by": "carol",
    },
    {
        "key": "fireship",
        "content_name": "Fireship",
        "type": "youtube",
        "release_year": 2017,
        "total_seasons": None,
        "total_episodes": None,
        "description": "High-intensity code tutorials and tech explainers for the modern web developer.",
        "cover_url": "https://i.ytimg.com/vi/9OQ5vaYbGV0/hqdefault.jpg",
        "link_url": "https://www.youtube.com/watch?v=JfPWbttemYE",
        "is_private": False,
        "created_by": "alice",
    },
    {
        "key": "lex",
        "content_name": "The Lex Fridman Podcast",
        "type": "podcast",
        "release_year": 2018,
        "total_seasons": None,
        "total_episodes": None,
        "description": "Long-form conversations with scientists, engineers, entrepreneurs, and philosophers about the nature of intelligence, consciousness, and the human condition.",
        "cover_url": "https://img.podimo.com/artwork/aHR0cHM6Ly9sZXhmcmlkbWFuLmNvbS93b3JkcHJlc3Mvd3AtY29udGVudC91cGxvYWRzL3Bvd2VycHJlc3MvYXJ0d29ya18zMDAwLTIzMC5wbmc?w=400&h=400&id=0259700c-20db-4a58-9c4c-5c649d59cf7b&type=PODCAST&s=alLWWmG7yYNe1K4Vh1yIghvXCfg=",
        "link_url": None,
        "is_private": False,
        "created_by": "bob",
    },

    {
        "key": "bob_private",
        "content_name": "Severance",
        "type": "tv",
        "release_year": 2022,
        "total_seasons": 2,
        "total_episodes": 19,
        "description": "Employees at a mysterious corporation undergo a procedure that surgically separates their work and personal memories.",
        "cover_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhDquTAvzwrFGZqFPZ_8r_MBFP64HCMzk3SbbLbxgiEorGtRb75_qErWNmsuKolzjTCQnP&s=10",
        "link_url": None,
        "is_private": True,
        "created_by": "bob",
    },
    {
        "key": "carol_private",
        "content_name": "Vinland Saga",
        "type": "anime",
        "release_year": 2019,
        "total_seasons": 2,
        "total_episodes": 48,
        "description": "A young Viking warrior seeks revenge against the man who killed his father, gradually questioning the very ideals he was raised on.",
        "cover_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoYjLSrB31aVvik3mfbRBI7fpVJsU--4jcfYUK_NOVvUQ5ZuvwF9z00HbbI3KGVxQ72rcr1A&s=10",
        "link_url": None,
        "is_private": True,
        "created_by": "carol",
    },
]

TRACKING = [
    {"username": "alice", "content_key": "breaking_bad", "status": "watching",   "current_season": 2,    "current_episode": 15},
    {"username": "alice", "content_key": "inception",    "status": "completed",  "current_season": None, "current_episode": None},
    {"username": "alice", "content_key": "aot",          "status": "watching",   "current_season": 1,    "current_episode": 5},
    {"username": "bob",   "content_key": "breaking_bad", "status": "completed",  "current_season": 5,    "current_episode": 62},
    {"username": "bob",   "content_key": "aot",          "status": "paused",     "current_season": 2,    "current_episode": 10},
    {"username": "bob",   "content_key": "lex",          "status": "watching",   "current_season": None, "current_episode": None},
    {"username": "bob",   "content_key": "bob_private",  "status": "watching",   "current_season": 1,    "current_episode": 4},
    {"username": "carol", "content_key": "breaking_bad", "status": "watching",   "current_season": 1,    "current_episode": 1},
    {"username": "carol", "content_key": "inception",    "status": "completed",  "current_season": None, "current_episode": None},
    {"username": "carol", "content_key": "aot",          "status": "completed",  "current_season": 4,    "current_episode": 87},
    {"username": "carol", "content_key": "carol_private","status": "watching",   "current_season": 1,    "current_episode": 6},
]

REVIEWS = [
    {"username": "alice", "content_key": "breaking_bad", "stars": 5, "body": "One of the greatest shows ever made. The character development is completely unmatched."},
    {"username": "bob",   "content_key": "breaking_bad", "stars": 5, "body": "An absolute masterpiece. Every season raises the stakes higher."},
    {"username": "carol", "content_key": "breaking_bad", "stars": 4, "body": "Brilliant writing throughout, just a slightly slow start to the first season."},
    {"username": "alice", "content_key": "inception",    "stars": 5, "body": "Mind-bending and visually stunning. Nolan at his absolute best."},
    {"username": "carol", "content_key": "inception",    "stars": 5, "body": "A true cinematic masterpiece. Gets better every time you rewatch it."},
    {"username": "bob",   "content_key": "aot",          "stars": 4, "body": "Incredible story with jaw-dropping animation. The last season is divisive but I loved it."},
    {"username": "carol", "content_key": "aot",          "stars": 5, "body": "The best anime I have ever watched. The finale left me completely speechless."},
    {"username": "alice", "content_key": "fireship",     "stars": 5, "body": "The best tech channel on YouTube. Learns you 100 things in 10 minutes."},
    {"username": "bob",   "content_key": "lex",          "stars": 3, "body": "Hit or miss depending on the guest, but the best episodes are genuinely great."},
    {"username": "alice", "content_key": "lex",          "stars": 4, "body": "Long but worthwhile. The episodes with scientists are especially good."},
]


def seed():
    with psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row) as conn:
        print("Seeding users...")
        user_ids = {}
        for u in USERS:
            row = conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id",
                (u["username"], u["email"], generate_password_hash(u["password"])),
            ).fetchone()
            user_ids[u["username"]] = row["user_id"]
            print(f"  {u['username']} (id={row['user_id']})")
        conn.commit()

        print("Seeding content...")
        content_ids = {}
        for item in CONTENT:
            uid = user_ids[item["created_by"]]
            conn.execute("SELECT set_config('app.current_user_id', %s, false)", (str(uid),))
            row = conn.execute(
                """
                INSERT INTO content
                    (content_name, created_by, type, release_year, total_seasons,
                     total_episodes, description, cover_url, link_url, is_private)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING content_id
                """,
                (
                    item["content_name"], uid, item["type"], item["release_year"],
                    item["total_seasons"], item["total_episodes"], item["description"],
                    item["cover_url"], item["link_url"], item["is_private"],
                ),
            ).fetchone()
            content_ids[item["key"]] = row["content_id"]
            tag = "private" if item["is_private"] else "public"
            print(f"  [{tag}] {item['content_name']} (id={row['content_id']})")
        conn.commit()

        print("Seeding tracking...")
        for t in TRACKING:
            uid = user_ids[t["username"]]
            conn.execute("SELECT set_config('app.current_user_id', %s, false)", (str(uid),))
            conn.execute(
                """
                INSERT INTO user_content (user_id, content_id, status, current_season, current_episode)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (uid, content_ids[t["content_key"]], t["status"], t["current_season"], t["current_episode"]),
            )
            print(f"  {t['username']} -> {t['content_key']} ({t['status']})")
        conn.commit()

        print("Seeding reviews...")
        for r in REVIEWS:
            uid = user_ids[r["username"]]
            conn.execute("SELECT set_config('app.current_user_id', %s, false)", (str(uid),))
            conn.execute(
                "INSERT INTO reviews (user_id, content_id, stars, body) VALUES (%s, %s, %s, %s)",
                (uid, content_ids[r["content_key"]], r["stars"], r["body"]),
            )
            print(f"  {r['username']} -> {r['content_key']} ({r['stars']}★)")
        conn.commit()

        print("\nDone. Login credentials (password: password123):")
        for u in USERS:
            print(f"  username: {u['username']}  /  email: {u['email']}")


if __name__ == "__main__":
    seed()
