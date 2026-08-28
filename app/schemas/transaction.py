import typing
from datetime import datetime

from pydantic import BaseModel

from app.schemas.enums import CurrencyEnum, TransactionStatusEnum


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: float


class TransactionModel(BaseModel):
    id: typing.Optional[int]
    user_id: typing.Optional[int] = None
    currency: typing.Optional[CurrencyEnum] = None
    amount: typing.Optional[float] = None
    status: typing.Optional[TransactionStatusEnum] = None
    created: typing.Optional[datetime] = None