from enum import Enum


class Error(str, Enum):
    NOT_FOUND = "Item not found"
    PASSWORD_WEAK = "The password must contain numbers, letters in both cases and special characters"
    USER_EXISTS = "User already exists"
    USER_NOT_FOUND = "User not found"
    INVALID_PASSWORD = "Invalid password"


class NotificationType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    REPOST = "repost"
