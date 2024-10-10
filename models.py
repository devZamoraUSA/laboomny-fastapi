from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class FormData(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    birthday_date: str
    options: str = Field(..., min_length=1)
    number_of_guests: int = Field(..., gt=0)
    special_notes: Optional[str]
    success_url: str
    cancel_url: str
