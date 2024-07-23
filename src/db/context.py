from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.models.db import Base
from src.constants import DB_CONNECTION_STRING

if not DB_CONNECTION_STRING:
    raise Exception("DB connection string not provided")

# SQLite connection string, e.g., "sqlite:///./test.db"
engine = create_engine(DB_CONNECTION_STRING, echo=False, pool_pre_ping=True)
session_maker = sessionmaker(bind=engine, expire_on_commit=False)

def create_db() -> None:
    Base.metadata.create_all(engine)

def get_db() -> Generator[Session, Any, None]:
    with session_maker() as session:
        yield session

def auto_create_db():
    try:
        con = engine.connect()
        create_db()
        con.close()
    except Exception as _:
        # SQLite does not require separate database creation
        create_db()
