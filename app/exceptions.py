class AppException(Exception):
    status_code: int = 400
    default_detail: str = "Bad request"

    def __init__(self, detail: str | None = None, status_code: int | None = None) -> None:
        self.detail = detail if detail is not None else self.default_detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


class UserAlreadyExistsException(AppException):
    status_code = 409
    default_detail = "User already exists"


class UserNotExistsException(AppException):
    status_code = 404
    default_detail = "User not found"


class UserAlreadyBlockedException(AppException):
    status_code = 400
    default_detail = "User already blocked"


class UserAlreadyActiveException(AppException):
    status_code = 400
    default_detail = "User already active"


class UserIsBlockedException(AppException):
    status_code = 403
    default_detail = "User is blocked"


class NotAuthenticatedException(AppException):
    status_code = 401
    default_detail = "Not authenticated"


class InvalidTokenException(AppException):
    status_code = 401
    default_detail = "Invalid token"


class TokenExpiredException(AppException):
    status_code = 401
    default_detail = "Token expired"


class InvalidCredentialsException(AppException):
    status_code = 401
    default_detail = "Invalid email or password"


class AdminRoleRequiredException(AppException):
    status_code = 403
    default_detail = "Admin role required"


class BadRequestDataException(AppException):
    status_code = 400
    default_detail = "Bad request data"


class NegativeBalanceException(AppException):
    status_code = 400
    default_detail = "Negative balance"


class TransactionNotExistsException(AppException):
    status_code = 404
    default_detail = "Transaction not found"


class TransactionDoesNotBelongToUserException(AppException):
    status_code = 403
    default_detail = "Transaction does not belong to user"


class CreateTransactionForBlockedUserException(AppException):
    status_code = 403
    default_detail = "Cannot create transaction for blocked user"


class UpdateTransactionForBlockedUserException(AppException):
    status_code = 403
    default_detail = "Cannot update transaction for blocked user"


class TransactionAlreadyRollbackedException(AppException):
    status_code = 400
    default_detail = "Transaction already rollbacked"


class TransactionZeroAmountException(AppException):
    status_code = 422
    default_detail = "Transaction can not have zero amount"


class BalanceNotFoundException(AppException):
    status_code = 404
    default_detail = "Balance for requested currency not found"
