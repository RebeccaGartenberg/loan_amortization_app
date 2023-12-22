from typing import Union

from pydantic import BaseModel


class LoanBase(BaseModel):
    amount: float
    annual_interest_rate: float
    loan_term: int
    type: Union[str, None] = None


class LoanCreate(LoanBase):
    pass


class Loan(LoanBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    type: Union[str, None] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    loans: list[Loan] = []

    class Config:
        orm_mode = True
