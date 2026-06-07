# seriesly

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

3. **Create a `.env` file** (copy from the example and fill in your values)
   ```
   cp .env.example .env
   ```
   Edit `.env`:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/seriesly
   ```

4. **Create the database** (one-time)
   ```
   psql -U postgres -c "CREATE DATABASE seriesly;"
   ```

5. **Initialize the schema** (one-time)
   ```
   flask --app run init-db
   ```
6. **Seed the database** (optional)
   ```
   python seed.py
   ```

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

1. **Start the containers** (builds the app image, starts PostgreSQL, initializes the schema)
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
