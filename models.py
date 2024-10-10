from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime

class FormData(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    birthday_date: str  # Puede ser 'date' o 'str'
    options: str = Field(..., min_length=1)
    number_of_guests: int = Field(..., gt=0)
    special_notes: Optional[str]
    submission_datetime: datetime
    success_url: str
    cancel_url: str

    @validator('submission_datetime')
    def validate_submission_datetime(cls, value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError('submission_datetime must be in ISO format')
        return value
