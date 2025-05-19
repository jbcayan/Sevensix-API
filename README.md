# FastAPI Project Template 


Project structure
```
istandard/
├── Dockerfile
├── docker-compose.yml
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── app/
│   ├── main.py
│   ├── accounts/
│   │   ├── auth.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── config/
│   │   ├── database.py
│   │   └── settings.py
├── utils/
├── requirements.txt
├── .env.example
└── README.md
```

# How to run the project

```bash
pip install -r requirements.txt
alembic upgrade head

```
```bash
uvicorn app.main:app --reload
```

<hr>
<hr>

### Alembic Commands
Here are the commands you will use for managing migrations in your project:

Create a Migration File (equivalent to Django's makemigrations): After making changes to your models (e.g., adding a new field to your user model), run this command to generate the migration file:
```bash
alembic revision --autogenerate -m "Add created_at field to User model"
```

This command will generate a migration script in the alembic/versions/ directory with the given message ("Add created_at field to User model").

The migration file will contain the changes to your database schema (e.g., adding or altering tables, columns, etc.).

Apply the Migrations (equivalent to Django's migrate): To apply the migrations and update the database, run this command:

```bash
alembic upgrade head
```
This will apply the migrations to the most recent revision (head), ensuring that the database schema is up to date.

<hr>

### Example Downgrade Commands:
Downgrade all migrations (rollback to the initial state):

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
<hr>


### ✅ Alembic Migration Setup
After building the image and container:

```bash
docker-compose run api alembic init alembic
docker-compose run api alembic revision --autogenerate -m "create users table"
docker-compose run api alembic upgrade head
```

### ✅ Delete Pycache Files
Windows powershell: 

```bash
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```
macOS/Linux: 
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```