import typing
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.enums import CurrencyEnum, UserStatusEnum


class RequestUserRegisterModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RequestUserLoginModel(BaseModel):
    email: EmailStr
    password: str


class RequestRefreshTokenModel(BaseModel):
    refresh_token: str


class RequestUserUpdateModel(BaseModel):
    status: UserStatusEnum


class ResponseUserBalanceModel(BaseModel):
    currency: typing.Optional[CurrencyEnum] = None
    amount: typing.Optional[float] = None


class ResponseUserModel(BaseModel):
    id: typing.Optional[int]
    email: typing.Optional[str] = None
    status: typing.Optional[UserStatusEnum] = None
    created: typing.Optional[datetime] = None
    balances: typing.Optional[typing.List[ResponseUserBalanceModel]] = None


class UserModel(BaseModel):
    id: typing.Optional[int]
    email: typing.Optional[str] = None
    status: typing.Optional[UserStatusEnum] = None
    created: typing.Optional[datetime] = None


class UserBalanceModel(BaseModel):
    id: typing.Optional[int]
    user_id: typing.Optional[int] = None
    currency: typing.Optional[CurrencyEnum] = None
    amount: typing.Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def validate_not_negative(cls, values):
        if isinstance(values, dict):
            amount = values.get("amount")
            if amount is not None and amount < 0:
                raise ValueError("Amount cannot be negative")
        return values


class TokenResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
