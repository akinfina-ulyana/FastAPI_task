from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, DateTime, ForeignKey, Numeric, String, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.schemas.enums import UserRoleEnum, UserStatusEnum


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    status: Mapped[UserStatusEnum] = mapped_column(
        Enum(UserStatusEnum, native_enum=False, length=20),
        default=UserStatusEnum.ACTIVE.value,
        server_default=UserStatusEnum.ACTIVE.value,
        )
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum, native_enum=False, length=20),
        default=UserRoleEnum.USER.value,
        server_default=UserRoleEnum.USER.value,
    )
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_balance: Mapped[list["UserBalance"]] = relationship(back_populates="owner", cascade="all, delete-orphan",)


class UserBalance(Base):
    __tablename__ = "user_balance"
    __table_args__ = (
        UniqueConstraint("user_id", "currency", name="user_balance_user_currency_unique"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    currency: Mapped[str] = mapped_column(String)
    amount: Mapped[Decimal] = mapped_column(Numeric, default=0, server_default="0")
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="user_balance")