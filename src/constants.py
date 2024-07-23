from sqlalchemy import create_engine, inspect, text
from datetime import timedelta

DB_CONNECTION_STRING = "sqlite:///./raspiweb.db"
engine = create_engine(DB_CONNECTION_STRING, echo=True)

# Verificar si la tabla existe
inspector = inspect(engine)
if not inspector.has_table("users"):
    with engine.connect() as connection:
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """))
    print("Table created successfully")
else:
    print("Table already exists")

# Aquí definimos COOKIES_KEY_NAME
COOKIES_KEY_NAME = "session_token"
SESSION_TIME = timedelta(days=30)
