from ninja import Schema, Field
from datetime import datetime
from pydantic import BaseModel, Field, constr, EmailStr


class PostIn(Schema):

    """
    Schema for input data when creating a new blog post.

    """

    title: constr(min_length=1)
    content: constr(min_length=1)
    auto_reply_enabled: bool = False
    auto_reply_delay: int = 0
    auto_reply_text: str = ""


class PostOut(Schema):

    """
    Schema for output data representing a blog post.

    """

    id: int
    title: str
    content: str
    created_at: datetime


class CommentIn(Schema):
    """
    Schema for input when creating a new comment.

    """
    content: str


class CommentOut(Schema):
    """
    Schema for output data representing a comment.

    """

    id: int
    post_id: int
    content: str
    author_id: int
    created_at: str  # Убедитесь, что это строка
    is_blocked: bool

    @classmethod
    def from_orm(cls, obj):

        """

        Create an instance of CommentOut from a Django model instance.

        """
        return cls(
            id=obj.id,
            post_id=obj.post.id,
            content=obj.content,
            author_id=obj.author.id,
            created_at=obj.created_at.isoformat(),
            is_blocked=obj.is_blocked
        )


class UserRegistration(Schema):

    """
    Schema for input data when registering a new user.


    """

    username: constr(min_length=1)
    password: constr(min_length=6)
    email: EmailStr


class UserResponse(Schema):
    """
    Schema for output data after user registration.

    """

    id: int
    username: str
    email: str


class UserLogin(Schema):
    """
    Schema for input data when a user logs in.

    """
    username: str
    password: str


class Token(Schema):

    """
    Schema for output data representing a token.

    """

    token: str
