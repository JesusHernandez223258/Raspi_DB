from sqlalchemy import Delete, Update
from sqlalchemy.sql.functions import current_timestamp

from src.models.db import User
from src.db.context import session_maker

def add(name: str, surname: str, role: User.Role, email: str, password: str) -> User:
    with session_maker.begin() as session:
        user = User(name=name, surname=surname, role=role, email=email, password=password)
        session.add(user)
        session.flush()
        return user

def update(id: int, name: str, surname: str, role: User.Role, email: str, password: str) -> None:
    with session_maker.begin() as session:
        session.execute(Update(User).where(User.id == id).values({
            User.name: name,
            User.surname: surname,
            User.role: role,
            User.email: email,
            User.password: password,
            User.updated_at: current_timestamp()
        }))

def delete(id: int) -> None:
    with session_maker.begin() as session:
        session.execute(Delete(User).where(User.id == id))
    
def get(limit: int = 1000, offset: int = 0) -> list[User]:
    with session_maker() as session:
        return session.query(User).limit(limit).offset(offset).all()

def get_by_id(id: int) -> User | None:
    with session_maker() as session:
        return session.query(User).where(User.id == id).first()

def get_by_email(email: str) -> User | None:
    with session_maker.begin() as session:
        return session.query(User).where(User.email == email).first()
