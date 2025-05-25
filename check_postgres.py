import psycopg2
import sys

# Database connection parameters
params = {
    "host": "localhost",  # Using localhost for this check
    "port": "5432",
    "user": "postgres",
    "password": "2244",
    "database": "sevensix_db"
}

try:
    # Try to connect to the database
    print(f"Attempting to connect to PostgreSQL at {params['host']}:{params['port']} as {params['user']}...")
    conn = psycopg2.connect(**params)

    # If successful, print a success message
    print("Connection successful!")

    # Get server version
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"PostgreSQL version: {version}")

    # Close the connection
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)