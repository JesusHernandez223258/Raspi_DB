from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from src.models import db
from src.services import jwt_service, user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def user_dependency(request: Request, token: str = Depends(oauth2_scheme)) -> db.User:
    # Extraer token de las cookies si se pasa en lugar del encabezado
    if not token:
        token = request.cookies.get("X-SESSION", "")

    data = jwt_service.decode(token)
    if data is None:
        raise HTTPException(status_code=401, detail="Token is invalid")

    user = user_service.get_by_id(data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
