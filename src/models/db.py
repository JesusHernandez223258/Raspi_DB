from enum import StrEnum
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column("id", Integer(), primary_key=True, autoincrement=True)
    name = Column("name", String(32))
    surname = Column("surname", String(32))
    role = Column("role", String(32))
    email = Column("email", String(256), unique=True)
    password = Column("password", String(256))
    updated_at = Column("updated_at", DateTime(), default=current_timestamp())
    created_at = Column("created_at", DateTime(), default=current_timestamp())

    class Role(StrEnum):
        ADMIN = "admin"
        USER = "user"
        GUEST = "guest"
