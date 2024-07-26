from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from ..utils import formating
from ..models import db, dto
from ..services import user_service, jwt_service
from ..utils.bcrypt_hashing import HashLib
from ..utils import dependencies
from ..constants import COOKIES_KEY_NAME, SESSION_TIME

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dto.GetUser)
async def register(user: dto.CreateUser):
    try:
        email = formating.format_string(user.email)
        
        if not email:
            raise HTTPException(
                detail="Email cannot be empty",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        if not user.password:
            raise HTTPException(
                detail="Password cannot be empty",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        exist_user = user_service.get_by_email(email)
        if exist_user:
            raise HTTPException(
                detail=f"User '{email}' already exists",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        created_user = user_service.create(
            user.name,
            user.surname,
            db.User.Role.USER,
            email,
            user.password
        )
        return created_user
    
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/login", status_code=status.HTTP_200_OK, response_model=str)
async def login(dto: dto.LoginUser, res: Response):
    try:
        NOW = datetime.now(timezone.utc)
        email = formating.format_string(dto.email)
        
        user = user_service.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not HashLib.validate(dto.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
        
        exp_date = NOW + SESSION_TIME
        token = jwt_service.encode(user.id, user.role, exp_date)
        res.set_cookie(COOKIES_KEY_NAME, token, expires=exp_date)
        return token

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(res: Response):
    try:
        res.delete_cookie(COOKIES_KEY_NAME)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/validate", response_model=dto.Token)
async def check_session(req: Request, res: Response):
    try:
        token = req.cookies.get(COOKIES_KEY_NAME, "")
        data = jwt_service.decode(token)
        
        if data is None:
            res.delete_cookie(COOKIES_KEY_NAME)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
        
        return data
    
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.put("/password/update", status_code=status.HTTP_204_NO_CONTENT)
def update_password(dto: dto.UpdateUserPass, user: dependencies.user_dependency):
    try:
        if dto.old_password == dto.new_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Passwords cannot be the same")
        
        if not HashLib.validate(dto.old_password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
        
        user_service.update_password(user.id, dto.new_password)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/password/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(email: str):
    try:
        user = user_service.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        new_pass = user_service.reset_password(user.id)
        print(f"User {user.email} new password: {new_pass}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
