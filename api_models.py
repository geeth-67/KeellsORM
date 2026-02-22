from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):

    name : str = Field(...,min_length=3, max_length=255)
    email : str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):

    name : Optional[str] = Field(..., min_length=3 , max_length=255)
    email : Optional[str] = None

class UserResponse(UserBase):

    id : int

    class Config:
        form_attributes = True


#------------------------------------------------------------------------------#


class InvoiceBase(BaseModel):

    user_id: int
    amount: float = Field(...,gt=0)
    description: str = Field(...,max_length=400)

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(InvoiceBase):

    amount: Optional[int] = Field(None,gt=0)
    description: Optional[str] = Field(None,max_length=400)

class InvoiceResponse(InvoiceBase):

    id: int
    created_at: datetime

    class Config:
        form_attributes = True