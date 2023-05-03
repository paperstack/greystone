from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from pydantic.fields import Field


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    
class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    loans: list[Loan] | None = None
    class Config:
        orm_mode = True

class LoanMonth(BaseModel):
    id: int
    month: int
    principal_amount: float
    interest_amount: float
    class Config:
        orm_mode = True
    
      
class LoanBase(BaseModel):
    amount: float = Field(gt=0, description="The principal must be greater than zero")
    term: int = Field(gt=0, description="The term must be greater than zero")
    interest_rate: float = Field(ge=0, description="The interest rate must not be less than zero")
    
class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: int
    loan_months: list[LoanMonth] = []
    users: list[User] = []
    class Config:
        orm_mode = True
        
class ScheduleItem(BaseModel):
    month: int = Field(gt=0, description="The month must be greater than zero")
    remaining_balance: float = Field(ge=0, description="The remaining balance cannot be negative")
    monthly_payment: float = Field(gt=0, description="The monthly payment must be greater than zero")

        
User.update_forward_refs()