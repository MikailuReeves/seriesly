# seriesly

## Running locally

### Prerequisites
- Python 3.x
- PostgreSQL (running on localhost:5432)

### Setup

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** (copy from the example and fill in your values)
   ```
   cp .env.example .env
   ```
   Edit `.env`:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/seriesly
   ```

3. **Create the database** (one-time)
   ```
   psql -U postgres -c "CREATE DATABASE seriesly;"
   ```

4. **Initialize the schema** (one-time)
   ```
   flask --app run init-db
   ```
5. **Seed the database** (optional)
   ```
   python seed.py
   ```

6. **Start the dev server**
   ```
   python run.py
   ```
   App runs at http://localhost:5000.
