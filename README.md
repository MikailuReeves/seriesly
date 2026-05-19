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

2. **Create the database** (one-time)
   ```
   psql -U postgres -c "CREATE DATABASE seriesly;"
   ```

3. **Set the database URL** (required every new terminal session)
   ```powershell
   $env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost/seriesly"
   ```

4. **Initialize the schema** (one-time)
   ```
   flask --app run init-db
   ```

5. **Start the dev server**
   ```
   python run.py
   ```
   App runs at http://localhost:5000.
