from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user, get_transaction_service
from app.exceptions import BadRequestDataException
from app.models import Transaction, User
from app.schemas import RequestTransactionModel, TransactionModel
from app.schemas.enums import UserRoleEnum
from app.services.transaction import TransactionService

router = APIRouter(tags=["transactions"])


@router.get(
    "/transactions",
    response_model=list[TransactionModel],
    status_code=status.HTTP_200_OK,
)
async def get_transactions(
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> list[Transaction]:
    is_admin = current_user.role == UserRoleEnum.ADMIN
    if user_id is None:
        if is_admin:
            return await transaction_service.get_all_transactions()
        return await transaction_service.get_user_transactions(current_user.id)
    if not is_admin and user_id != current_user.id:
        raise BadRequestDataException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unprocessable user",
        )
    return await transaction_service.get_user_transactions(user_id)


@router.get(
    "/users/{user_id}/transactions",
    response_model=list[TransactionModel],
    status_code=status.HTTP_200_OK,
)
async def get_user_transactions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> list[Transaction]:
    if user_id <= 0:
        raise BadRequestDataException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable data in request",
        )
    is_admin = current_user.role == UserRoleEnum.ADMIN
    if not is_admin and user_id != current_user.id:
        # non-admin cannot read other users' transactions
        raise BadRequestDataException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unprocessable user",
        )
    return await transaction_service.get_user_transactions(user_id)


@router.post(
    "/users/{user_id}/transactions",
    response_model=TransactionModel,
    status_code=status.HTTP_201_CREATED,
)
async def post_transaction(
    user_id: int,
    transaction: RequestTransactionModel,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> Transaction:
    if user_id <= 0:
        raise BadRequestDataException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable data in request",
        )
    if current_user.id != user_id:
        raise BadRequestDataException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unprocessable user",
        )
    return await transaction_service.create_transaction(current_user, transaction)


@router.patch(
    "/users/{user_id}/transactions/{transaction_id}",
    response_model=TransactionModel,
)
async def patch_rollback_transaction(
    user_id: int,
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
) -> Transaction:
    if user_id <= 0 or transaction_id <= 0:
        raise BadRequestDataException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable data in request",
        )
    if current_user.id != user_id:
        raise BadRequestDataException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unprocessable user",
        )
    return await transaction_service.rollback_transaction(current_user, transaction_id)
