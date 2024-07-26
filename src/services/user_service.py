from sqlalchemy.orm import Session

from ..models.db import User
from ..db.context import get_db
from ..utils.bcrypt_hashing import HashLib
from ..db import user_db

def create(name: str, surname: str, role: User.Role, email: str, password: str) -> User:
    hashed_password = HashLib.hash(password)
    return user_db.add(name, surname, role, email, hashed_password)

def get_by_email(email: str) -> User | None:
    return user_db.get_by_email(email)

def get_by_id(id: int) -> User | None:
    return user_db.get_by_id(id)

def update_password(id: int, new_password: str) -> None:
    hashed_password = HashLib.hash(new_password)
    user_db.update(id, None, None, None, hashed_password)

def update_name_surname(id: int, name: str, surname: str) -> None:
    user_db.update(id, name, surname, None, None)

def delete(id: int) -> None:
    user_db.delete(id)

def reset_password(id: int) -> str:
    new_password = "new_password"  # Generate a new password in a real-world scenario
    hashed_password = HashLib.hash(new_password)
    user_db.update(id, None, None, None, hashed_password)
    return new_password
