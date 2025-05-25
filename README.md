# Sevensix API
A scalable backend API built with FastAPI, structured with modular apps, Alembic for database migrations, and Docker support for seamless development and deployment.


📁 Project Structure
```
Sevensix-API/
├── alembic/                 # Alembic migration environment
│   ├── README
│   ├── script.py.mako
│   └── versions/
├── alembic.ini              # Alembic configuration file
├── app/                     # Main application directory
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── accounts/            # Accounts module
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── permissions.py
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── services/
│   ├── chat/                # Chat module
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   └── config/              # Configuration settings
│       ├── __init__.py
│       ├── database.py
│       └── settings.py
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Dockerfile for containerization
├── LICENSE
├── private_chroma_db/       # Private ChromaDB instance
│   └── chroma.sqlite3
├── public_chroma_db/        # Public ChromaDB instance
│   └── chroma.sqlite3
├── README.md                # Project documentation
```

### 🚀 Getting Started
1. Install Dependencies
```bash
  pip install -r requirements.txt
```
2. Run the Server Locally
```bash
  uvicorn app.main:app --reload
```
### or
Run the Server in Docker
```bash
  docker compose up --build
```
This will start the development server on http://127.0.0.1:8000.

<hr>
<hr>

### ⚙️ Database Migrations
Create a Migration
Equivalent to Django’s makemigrations. After modifying your models:

```bash
alembic revision --autogenerate -m "Add created_at field to User model"
```

Apply Migrations

You typically do not need to run this manually. Migrations are automatically applied when the server starts, as handled in main.py.
However, you can manually run it using:
```bash
alembic upgrade head
```
<hr>

### 🧯 Downgrade Migrations
Revert all migrations:

```bash
alembic downgrade base
```
Downgrade to a specific revision (e.g., revision ID 1234567890ab):
```bash
alembic downgrade 1234567890ab
```
Downgrade one step back:
```bash
alembic downgrade -1
```
<hr>

### 🧹 Clear __pycache__ Files
If you're encountering issues due to Python’s caching mechanism, you can remove all __pycache__ directories.

For Windows (PowerShell):
```bash
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```
macOS/Linux: 
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```