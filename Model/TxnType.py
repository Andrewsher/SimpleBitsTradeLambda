import enum
class TxnType(enum.Enum):
    SELL = "SELL"
    BUY = "BUY"
    CREATE_USER = "CREATE_USER"
    CLOSE_USER = "CLOSE_USER"
