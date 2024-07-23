from datetime import datetime
from pydantic import BaseModel, Field

# USER
class CreateUser(BaseModel):
    name: str
    surname: str
    email: str
    password: str = Field(..., min_length=4) 

class GetUser(BaseModel):
    id: int
    name: str
    surname: str
    role: str
    email: str
    updated_at: datetime
    created_at: datetime        
    
class UpdateUser(BaseModel):
    name: str
    surname: str
    
class LoginUser(BaseModel):
    email: str
    password: str
    
class UpdateUserPass(BaseModel):
    old_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=4)
    
# Token
class Token(BaseModel):
    user_id: int
    role: str
    exp: datetime
