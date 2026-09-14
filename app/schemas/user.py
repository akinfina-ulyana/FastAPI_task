from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.enums import CurrencyEnum, UserRoleEnum, UserStatusEnum


class RequestUserRegisterModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(ch.islower() for ch in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(ch.isupper() for ch in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("Password must contain at least one digit")
        return value


class RequestUserLoginModel(BaseModel):
    email: EmailStr
    password: str


class RequestRefreshTokenModel(BaseModel):
    refresh_token: str


class RequestUserUpdateModel(BaseModel):
    status: UserStatusEnum


class ResponseUserBalanceModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    currency: CurrencyEnum
    amount: Decimal


class ResponseUserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    status: UserStatusEnum
    role: UserRoleEnum
    created: datetime
    balances: list[ResponseUserBalanceModel] = Field(default_factory=list)


class TokenResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
