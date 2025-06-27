# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class InsertCredentialsRequest(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True
