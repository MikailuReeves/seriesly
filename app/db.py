import os

import click
import psycopg
from flask import current_app, g, has_request_context, session


def get_db():
    if "db" not in g:
        g.db = psycopg.connect(
            current_app.config["DATABASE_URL"],
            row_factory=psycopg.rows.dict_row,
        )
        if has_request_context():
            user_id = session.get("user_id")
            g.db.execute(
                "SELECT set_config('app.current_user_id', %s, false)",
                (str(user_id) if user_id is not None else "",),
            )
    return g.db


def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    with current_app.open_resource("schema.sql") as schema_file:
        schema_sql = schema_file.read().decode("utf-8")

    with psycopg.connect(current_app.config["DATABASE_URL"]) as db:
        db.execute(schema_sql)


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.config.setdefault(
        "DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql://localhost/seriesly"),
    )
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
