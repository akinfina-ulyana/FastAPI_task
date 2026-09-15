from app.core.security import hash_password
from app.core.uow import UnitOfWork
from app.exceptions import (
    BadRequestDataException,
    UserAlreadyActiveException,
    UserAlreadyBlockedException,
    UserAlreadyExistsException,
    UserNotExistsException,
)
from app.models import User
from app.schemas import (
    CurrencyEnum,
    RequestUserRegisterModel,
    ResponseUserBalanceModel,
    ResponseUserModel,
    UserStatusEnum,
)


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register_user(self, user_data: RequestUserRegisterModel) -> ResponseUserModel:
        email = user_data.email.strip()
        if not email:
            raise BadRequestDataException("Email can't be empty")
        existing_user = await self.uow.users.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsException("Please try another email")

        password_hash = hash_password(user_data.password)
        user = await self.uow.users.create_user(email, password_hash)
        currencies = [currency.value for currency in CurrencyEnum]
        await self.uow.users.create_user_balances(user.id, currencies)
        await self.uow.commit()

        created_user = await self.uow.users.get_user_by_id(user.id, with_balances=True)
        return self._to_response(created_user or user)

    async def get_all(
        self,
        user_id: int | None = None,
        email: str | None = None,
        user_status: UserStatusEnum | None = None,
    ) -> list[ResponseUserModel]:
        users = await self.uow.users.get_all(user_id=user_id, email=email, user_status=user_status)
        return [self._to_response(user) for user in users]

    async def get_by_id(self, user_id: int) -> ResponseUserModel:
        if user_id <= 0:
            raise BadRequestDataException("Unprocessable data in request")
        user = await self.uow.users.get_user_by_id(user_id, with_balances=True)
        if not user:
            raise UserNotExistsException(f"User with id=`{user_id}` does not exist")
        return self._to_response(user)

    async def get_profile(self, current_user: User) -> ResponseUserModel:
        user = await self.uow.users.get_user_by_id(current_user.id, with_balances=True)
        if not user:
            raise UserNotExistsException("Current user not found")
        return self._to_response(user)

    async def update_status(self, user_id: int, new_status: UserStatusEnum) -> ResponseUserModel:
        if user_id <= 0:
            raise BadRequestDataException("Unprocessable data in request")

        db_user = await self.uow.users.get_user_by_id(user_id, with_balances=True)
        if not db_user:
            raise UserNotExistsException(f"User with id=`{user_id}` does not exist")

        if db_user.status == UserStatusEnum.BLOCKED and new_status == UserStatusEnum.BLOCKED:
            raise UserAlreadyBlockedException(f"User with id=`{user_id}` is already blocked")
        if db_user.status == UserStatusEnum.ACTIVE and new_status == UserStatusEnum.ACTIVE:
            raise UserAlreadyActiveException(f"User with id=`{user_id}` is already active")

        await self.uow.users.update_status(user_id, new_status)
        db_user.status = new_status
        await self.uow.commit()
        return self._to_response(db_user)

    @staticmethod
    def _to_response(user: User) -> ResponseUserModel:
        balances = getattr(user, "user_balance", None)
        return ResponseUserModel(
            id=user.id,
            email=user.email,
            status=user.status,
            role=user.role,
            created=user.created,
            balances=[
                ResponseUserBalanceModel(
                    currency=CurrencyEnum(balance.currency), amount=balance.amount
                )
                for balance in (balances or [])
            ],
        )
