import enum
class UserStatus(enum.Enum):
    NORMAL = "NORMAL"
    CREATING = "CREATING"
    EXCEPTION = "EXCEPTION"
    CLOSED = "CLOSED"