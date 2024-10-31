import pytest
from pydantic import ValidationError
from datetime import datetime

from posts.schemas import (
    PostIn,
    PostOut,
    CommentIn,
    CommentOut,
    UserRegistration,
    UserResponse,
    UserLogin,
    Token
)


def test_post_in_schema():

    """Test the PostIn schema for valid input data."""

    data = {
        "title": "Sample Post",
        "content": "This is a sample post.",
        "auto_reply_enabled": True,
        "auto_reply_delay": 5,
        "auto_reply_text": "Thank you for your comment!",
    }

    post_in = PostIn(**data)

    assert post_in.title == "Sample Post"

    assert post_in.content == "This is a sample post."

    assert post_in.auto_reply_enabled is True


def test_post_out_schema():

    """Test the PostOut schema for valid output data."""

    data = {
        "id": 1,
        "title": "Sample Post",
        "content": "This is a sample post.",
        "created_at": datetime.now(),
    }

    post_out = PostOut(**data)

    assert post_out.id == 1

    assert post_out.title == "Sample Post"

    assert post_out.created_at is not None



def test_comment_in_schema():

    """Test the CommentIn schema for valid input data."""

    data = {
        "content": "This is a comment.",
    }

    comment_in = CommentIn(**data)

    assert comment_in.content == "This is a comment."


def test_comment_out_schema():

    """Test the CommentOut schema for valid output data."""

    data = {
        "id": 1,
        "post_id": 1,
        "content": "This is a comment.",
        "author_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "is_blocked": False,
    }

    comment_out = CommentOut(**data)

    assert comment_out.id == 1

    assert comment_out.post_id == 1

    assert comment_out.is_blocked is False


def test_user_registration_schema():

    """Test the UserRegistration schema for valid input data."""

    data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com",
    }

    user_registration = UserRegistration(**data)

    assert user_registration.username == "testuser"

    assert user_registration.email == "test@example.com"


def test_user_response_schema():

    """Test the UserResponse schema for valid output data."""

    data = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
    }

    user_response = UserResponse(**data)

    assert user_response.id == 1

    assert user_response.username == "testuser"


def test_user_login_schema():

    """Test the UserLogin schema for valid input data."""

    data = {
        "username": "testuser",
        "password": "password123",
    }

    user_login = UserLogin(**data)

    assert user_login.username == "testuser"


def test_token_schema():

    """Test the Token schema for valid output data."""

    data = {
        "token": "some.jwt.token",
    }
    token = Token(**data)

    assert token.token == "some.jwt.token"


def test_post_in_schema_invalid():

    """Test the PostIn schema for invalid input data."""

    with pytest.raises(ValidationError):

        PostIn(title="Sample Post", content="")


def test_user_registration_schema_invalid():

    """Test the UserRegistration schema for invalid input data."""

    with pytest.raises(ValidationError):

        UserRegistration(username="", password="password123", email="")
