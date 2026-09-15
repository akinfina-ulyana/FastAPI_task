from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import CurrencyEnum, TransactionStatusEnum


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal = Field(max_digits=20, decimal_places=8)


class TransactionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    currency: CurrencyEnum
    amount: Decimal
    status: TransactionStatusEnum
    created: datetime
