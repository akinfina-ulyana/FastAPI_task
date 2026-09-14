import enum


class CurrencyEnum(enum.Enum):
    USD = "USD"
    EUR = "EUR"
    AUD = "AUD"
    CAD = "CAD"
    ARS = "ARS"
    PLN = "PLN"
    BTC = "BTC"
    ETH = "ETH"
    DOGE = "DOGE"
    USDT = "USDT"


class UserStatusEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class UserRoleEnum(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class TransactionStatusEnum(enum.Enum):
    PROCESSED = "PROCESSED"
    ROLLBACKED = "ROLLBACKED"
