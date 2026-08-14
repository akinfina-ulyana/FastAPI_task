from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, func, ForeignKey
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.schemas.enums import TransactionStatusEnum


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    currency: Mapped[str] = mapped_column(String)
    amount: Mapped[Decimal] = mapped_column(Numeric)
    status: Mapped[TransactionStatusEnum] = mapped_column(Enum(TransactionStatusEnum, native_enum=False, length=20),
                                                          default=TransactionStatusEnum.PROCESSED.value,
                                                          server_default=TransactionStatusEnum.PROCESSED.value,
                                                          )
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()  # back_populates="user_transaction"
