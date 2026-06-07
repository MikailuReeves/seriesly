# Seriesly

A community-driven series tracker for TV shows, movies, anime, YouTube series, and podcasts. Users can add content to a shared catalogue, track watch progress, and write reviews. Built with Flask and PostgreSQL.

## Database model

![ER diagram](er_diagram.png)


## Running locally

### Prerequisites
- Python 3.x
- PostgreSQL (running on localhost:5432)

### Setup

1. **Create and activate a virtual environment**
```
   python -m venv .venv
```
   Windows:
```
   .venv\Scripts\activate
```
   macOS / Linux:
```
   source .venv/bin/activate
```

2. **Install dependencies**
```
   pip install -r requirements.txt
```

3. **Create a `.env` file**
```
   cp .env.example .env
```
   Edit `.env`:
```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/seriesly
```

4. **Create the database**
```
   psql -U postgres -c "CREATE DATABASE seriesly;"
```

5. **Initialize the schema**
```
   flask --app run init-db
```
   This creates all tables, functions, triggers, and RLS policies defined in `app/schema.sql`.

6. **Seed the database** (optional)
```
   python seed.py
```
   Inserts three users (`alice`, `bob`, `carol`), five public content entries, two private entries, tracking records, and reviews. All seed accounts use the password `password123`.

7. **Start the dev server**
```
   python run.py
```
   App runs at http://localhost:5000.

---

## Running with Docker (recommended)

### Prerequisites
- Docker and Docker Compose

### Setup

1. **Start the containers**
```
   docker compose up --build
```
   App runs at http://localhost:5000.

2. **Seed the database** (optional, in a second terminal)
```
   docker compose exec web python seed.py
```

3. **Stop the containers**
```
   docker compose down
```

---

## Using the app

- **Sign up / log in** at `/signup` and `/login`. Login accepts either username or email.
- **Add content** from the home page. All five types are supported: TV, movie, anime, YouTube, and podcast. YouTube entries require a URL.
- **Track progress** from any content detail page. Watch status and episode/season progress are recorded and displayed as a progress bar.
- **Reviews** can be posted on any content detail page. Average rating and review count are shown in the detail header.
- **Search** at `/search` finds content by name using PostgreSQL regular expression matching. Private content owned by other users is excluded.
- **Edit or delete** private content from its detail page.

---

## AI declaration

AI tools (Claude) were used during the development phase of this project, specifically for:

- **Debugging**: identifying and resolving errors in Python, SQL, and Flask application code.
- **Implementation assistance**: answering questions about Flask and PostgreSQL integration, primarily as a substitute for documentation lookup.
- **CSS and front-end styling**: generating CSS rules to achieve the desired visual design.

All output was reviewed and adapted before use. CSS suggestions were treated as a starting point and modified to fit the project's design. No output was copied directly without review and modification.
