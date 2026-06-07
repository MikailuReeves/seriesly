from dotenv import load_dotenv
load_dotenv()

from app import create_app


app = create_app()


if __name__ == "__main__":
    import os
    host = "0.0.0.0" if os.environ.get("DOCKER") else "127.0.0.1"
    app.run(debug=True, host=host)
