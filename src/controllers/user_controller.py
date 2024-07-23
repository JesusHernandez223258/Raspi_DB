from fastapi import APIRouter, Query, Path, HTTPException, status
from fastapi.responses import Response

from src.models import db, dto
from src.services import user_service
from src.utils import dependencies

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.get("/me", response_model=dto.GetUser)
def get_me(user: dependencies.user_dependency) -> db.User:
    try:
        return user
    except Exception as e:
        # Log the error if you have a logger setup
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/{id}", response_model=dto.GetUser)
def get_by_id(id: int = Path(..., ge=1)) -> db.User:
    try:
        user = user_service.get_by_id(id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        # Log the error if you have a logger setup
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.put("/update", response_model=dto.GetUser)
def update_user(dto: dto.UpdateUser, user: dependencies.user_dependency) -> db.User:
    try:
        user_service.update_name_surname(user.id, dto.name, dto.surname)
        updated_user = user_service.get_by_id(user.id)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found after update")
        return updated_user
    except HTTPException as http_error:
        raise http_error  # Re-raise the HTTPException if it's already handled
    except Exception as e:
        # Log the error if you have a logger setup
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int = Path(..., ge=1)):
    try:
        user = user_service.get_by_id(id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user_service.delete(id)
    except HTTPException as http_error:
        raise http_error  # Re-raise the HTTPException if it's already handled
    except Exception as e:
        # Log the error if you have a logger setup
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
