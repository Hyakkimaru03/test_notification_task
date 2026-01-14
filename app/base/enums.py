from enum import Enum
from typing import Dict


class Error(int, Enum):
    NOT_FOUND = 1
    PASSWORD_WEAK = 2
    USER_EXISTS = 3
    USER_NOT_FOUND = 4
    INVALID_PASSWORD = 5


# На случай если нужна интернационализация на беке
ErrorMessages: Dict[int, str] = {
    1: "Item not found",
    2: "The password must contain numbers, letters in both cases and special characters",
    3: "User already exists",
    4: "User not found",
    5: "Invalid password",
}


class NotificationType(str, Enum):
    LIKE = "Like"
    COMMENT = "Comment"
    REPOST = "Repost"
